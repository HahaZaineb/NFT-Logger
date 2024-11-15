from flask import Flask, render_template, request, jsonify, session
from web3 import Web3
from eth_utils import to_checksum_address
from datetime import datetime
from dotenv import load_dotenv
import os
from pathlib import Path
import requests
import sqlite3

# Print current working directory
print("Current working directory:", os.getcwd())

# Print all files in current directory
print("Files in directory:", os.listdir())

# Load .env file
load_dotenv()

# Get JWT and print its value
PINATA_JWT = os.getenv('PINATA_JWT')
print("Full JWT value:", PINATA_JWT)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))

# Initialize Web3
ALCHEMY_URL = os.getenv('ALCHEMY_URL')
web3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))

# Contract details
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
wallet_address = os.getenv('WALLET_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect_wallet', methods=['POST'])
def connect_wallet():
    data = request.json
    wallet_address = data.get('wallet_address')
    if not wallet_address:
        return jsonify({'error': 'No wallet address provided'}), 400
        
    session['wallet_address'] = wallet_address
    return jsonify({'message': 'Wallet connected successfully'})

def upload_to_ipfs(metadata):
    try:
        url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
        headers = {
            'Authorization': f'Bearer {PINATA_JWT}'
        }
        response = requests.post(url, json=metadata, headers=headers)
        
        if response.status_code == 200:
            ipfs_hash = response.json()['IpfsHash']
            return f'ipfs://{ipfs_hash}'
        else:
            print(f"Failed to upload to IPFS. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error uploading to IPFS: {str(e)}")
        return None

@app.route('/log_data', methods=['POST'])
def log_data():
    if 'wallet_address' not in session:
        return jsonify({'error': 'Please connect your wallet first'}), 401
        
    try:
        next_token_id = contract.functions.nextTokenId().call()
        
        description = request.form['description']
        timestamp_str = request.form['timestamp']
        timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M')
        timestamp = int(timestamp_dt.timestamp())
        
        metadata = {
            "name": f"Data Log NFT #{next_token_id}",
            "description": description,
            "image": "https://your-default-image-url.png",
            "external_url": "",
            "attributes": [
                {
                    "trait_type": "Timestamp",
                    "value": timestamp_dt.strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    "trait_type": "Data Type",
                    "value": "Log Entry"
                }
            ],
            "properties": {
                "timestamp": timestamp,
                "raw_description": description
            }
        }
        
        metadata_uri = upload_to_ipfs(metadata)
        if not metadata_uri:
            return jsonify({'error': 'Failed to upload metadata to IPFS'}), 500
        
        ipfs_hash = metadata_uri.replace('ipfs://', '')
        http_url = f'https://gateway.pinata.cloud/ipfs/{ipfs_hash}'
        
        user_address = to_checksum_address(session['wallet_address'])
        txn = contract.functions.mintDataLogNFT(user_address, metadata_uri).build_transaction({
            'from': wallet_address,
            'gas': 300000,
            'nonce': web3.eth.get_transaction_count(wallet_address)
        })
        
        signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        return jsonify({
            'message': 'NFT minted successfully!',
            'transaction_hash': tx_hash.hex(),
            'metadata_uri': metadata_uri,
            'view_url': http_url
        })
        
    except Exception as e:
        print(f"Error in log_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/search_by_id')
def search_by_id():
    try:
        search_id = request.args.get('id')
        if not search_id:
            return jsonify({'error': 'No ID provided'}), 400
            
        token_id = int(search_id)
        try:
            token_uri = contract.functions.tokenURI(token_id).call()
            http_url = token_uri.replace('ipfs://', 'https://gateway.pinata.cloud/ipfs/')
            return jsonify({
                'nfts': [{
                    'tokenId': token_id,
                    'tokenURI': http_url
                }]
            })
        except Exception as e:
            return jsonify({'nfts': []})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search_by_description')
def search_by_description():
    try:
        search_text = request.args.get('description', '').lower()
        if not search_text:
            return jsonify({'error': 'No description provided'}), 400
            
        user_address = to_checksum_address(session['wallet_address'])
        token_ids = contract.functions.getOwnedTokens(user_address).call()
        
        matching_nfts = []
        for token_id in token_ids:
            token_uri = contract.functions.tokenURI(token_id).call()
            http_url = token_uri.replace('ipfs://', 'https://gateway.pinata.cloud/ipfs/')
            
            try:
                response = requests.get(http_url)
                if response.status_code == 200:
                    metadata = response.json()
                    if search_text in metadata.get('description', '').lower():
                        matching_nfts.append({
                            'tokenId': token_id,
                            'tokenURI': http_url
                        })
            except Exception as e:
                print(f"Error fetching metadata for token {token_id}: {str(e)}")
                continue
                
        return jsonify({'nfts': matching_nfts})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search_by_timestamp')
def search_by_timestamp():
    try:
        search_timestamp = request.args.get('timestamp')
        if not search_timestamp:
            return jsonify({'error': 'No timestamp provided'}), 400
            
        search_dt = datetime.strptime(search_timestamp, '%Y-%m-%dT%H:%M')
        search_unix = int(search_dt.timestamp())
        
        user_address = to_checksum_address(session['wallet_address'])
        token_ids = contract.functions.getOwnedTokens(user_address).call()
        
        matching_nfts = []
        for token_id in token_ids:
            token_uri = contract.functions.tokenURI(token_id).call()
            http_url = token_uri.replace('ipfs://', 'https://gateway.pinata.cloud/ipfs/')
            
            try:
                response = requests.get(http_url)
                if response.status_code == 200:
                    metadata = response.json()
                    metadata_timestamp = metadata.get('properties', {}).get('timestamp')
                    if metadata_timestamp == search_unix:
                        matching_nfts.append({
                            'tokenId': token_id,
                            'tokenURI': http_url
                        })
            except Exception as e:
                print(f"Error fetching metadata for token {token_id}: {str(e)}")
                continue
                
        return jsonify({'nfts': matching_nfts})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)