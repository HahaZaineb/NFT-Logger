<<<<<<< HEAD
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

# Print all environment variables (be careful with sensitive data)
print("All environment variables loaded:", {k: v for k, v in os.environ.items() if 'PINATA' in k})

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with your secret key

# Initialize Web3
ALCHEMY_URL = os.getenv('ALCHEMY_URL')
web3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))
print("Connected to Sepolia via Alchemy")

# Contract details
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
CONTRACT_ABI =  [
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "approve",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "sender",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "ERC721IncorrectOwner",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "ERC721InsufficientApproval",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "approver",
				"type": "address"
			}
		],
		"name": "ERC721InvalidApprover",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			}
		],
		"name": "ERC721InvalidOperator",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "ERC721InvalidOwner",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "receiver",
				"type": "address"
			}
		],
		"name": "ERC721InvalidReceiver",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "sender",
				"type": "address"
			}
		],
		"name": "ERC721InvalidSender",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "ERC721NonexistentToken",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "recipient",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "logURI",
				"type": "string"
			}
		],
		"name": "mintDataLogNFT",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "OwnableInvalidOwner",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "OwnableUnauthorizedAccount",
		"type": "error"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "approved",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "Approval",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "bool",
				"name": "approved",
				"type": "bool"
			}
		],
		"name": "ApprovalForAll",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "_fromTokenId",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "_toTokenId",
				"type": "uint256"
			}
		],
		"name": "BatchMetadataUpdate",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "_tokenId",
				"type": "uint256"
			}
		],
		"name": "MetadataUpdate",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "previousOwner",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "OwnershipTransferred",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "renounceOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "safeTransferFrom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			},
			{
				"internalType": "bytes",
				"name": "data",
				"type": "bytes"
			}
		],
		"name": "safeTransferFrom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"internalType": "bool",
				"name": "approved",
				"type": "bool"
			}
		],
		"name": "setApprovalForAll",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "Transfer",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "transferFrom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "balanceOf",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "getApproved",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "getOwnedTokens",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "getTokenOwner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			}
		],
		"name": "isApprovedForAll",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "name",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "nextTokenId",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "ownerOf",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes4",
				"name": "interfaceId",
				"type": "bytes4"
			}
		],
		"name": "supportsInterface",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "symbol",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "tokenURI",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]  # Your contract ABI here
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Wallet details
wallet_address = os.getenv('WALLET_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')

def upload_to_ipfs(metadata):
    try:
        url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
        
        # Use the loaded JWT token
        headers = {
            'Authorization': f'Bearer {os.getenv("PINATA_JWT")}',
            'Content-Type': 'application/json'
        }
        
        print("Attempting IPFS upload...")
        print(f"Metadata being uploaded: {metadata}")
        
        response = requests.post(
            url,
            headers=headers,
            json=metadata
        )
        
        print(f"Pinata response status: {response.status_code}")
        print(f"Pinata response: {response.text}")
        
        if response.status_code == 200:
            ipfs_hash = response.json()["IpfsHash"]
            print(f"Successfully uploaded to IPFS with hash: {ipfs_hash}")
            return f"ipfs://{ipfs_hash}"
        else:
            print(f"Error uploading to IPFS: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error in upload_to_ipfs: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect_wallet', methods=['POST'])
def connect_wallet():
    wallet_address = request.json.get('wallet_address')
    if wallet_address:
        session['wallet_address'] = wallet_address
        return jsonify({'message': 'Wallet connected successfully'})
    return jsonify({'error': 'No wallet address provided'}), 400

@app.route('/check_auth')
def check_auth():
    return jsonify({'authenticated': 'wallet_address' in session})

@app.route('/log_data', methods=['POST'])
def log_data():
    if 'wallet_address' not in session:
        return jsonify({'error': 'Please connect your wallet first'}), 401
        
    try:
        next_token_id = contract.functions.nextTokenId().call()
        
        description = request.form['description']
        # Convert datetime string to Unix timestamp
        timestamp_str = request.form['timestamp']
        timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M')
        timestamp = int(timestamp_dt.timestamp())
        
        # Create metadata with standard NFT metadata format
        metadata = {
            "name": f"Data Log NFT #{next_token_id}",
            "description": description,
            "image": "https://your-default-image-url.png",  # Add a default image URL
            "external_url": "",  # Optional: Add if you have a website
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
        
        # Upload to IPFS
        metadata_uri = upload_to_ipfs(metadata)
        if not metadata_uri:
            return jsonify({'error': 'Failed to upload metadata to IPFS'}), 500
        
        # Convert IPFS URI to HTTP URL for viewing
        ipfs_hash = metadata_uri.replace('ipfs://', '')
        http_url = f'https://gateway.pinata.cloud/ipfs/{ipfs_hash}'
        
        # Mint the NFT
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
            'view_url': http_url,
            'etherscan_url': f'https://sepolia.etherscan.io/tx/{tx_hash.hex()}'
        })
        
    except Exception as e:
        print(f"Error in log_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_nfts')
def get_nfts():
    if 'wallet_address' not in session:
        return jsonify({'error': 'Please connect your wallet first'}), 401
        
    try:
        user_address = to_checksum_address(session['wallet_address'])
        token_ids = contract.functions.getOwnedTokens(user_address).call()
        
        nfts = []
        for token_id in token_ids:
            token_uri = contract.functions.tokenURI(token_id).call()
            # Convert IPFS URI to HTTP URL
            http_url = token_uri.replace('ipfs://', 'https://gateway.pinata.cloud/ipfs/')
            nfts.append({
                "tokenId": token_id,
                "tokenURI": http_url
            })
            
        return jsonify({"nfts": nfts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search_by_id')
def search_by_id():
    try:
        search_id = request.args.get('id')
        if not search_id:
            return jsonify({'error': 'No ID provided'}), 400
            
        token_id = int(search_id)
        # Verify token exists and get its URI
        try:
            token_uri = contract.functions.tokenURI(token_id).call()
            # Convert IPFS URI to HTTP URL
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
            
        # Get all tokens owned by the user
        user_address = to_checksum_address(session['wallet_address'])
        token_ids = contract.functions.getOwnedTokens(user_address).call()
        
        matching_nfts = []
        for token_id in token_ids:
            token_uri = contract.functions.tokenURI(token_id).call()
            http_url = token_uri.replace('ipfs://', 'https://gateway.pinata.cloud/ipfs/')
            
            # Fetch metadata from HTTP URL
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
            
        # Convert search timestamp to Unix timestamp
        search_dt = datetime.strptime(search_timestamp, '%Y-%m-%dT%H:%M')
        search_unix = int(search_dt.timestamp())
        
        # Get all tokens owned by the user
        user_address = to_checksum_address(session['wallet_address'])
        token_ids = contract.functions.getOwnedTokens(user_address).call()
        
        matching_nfts = []
        for token_id in token_ids:
            token_uri = contract.functions.tokenURI(token_id).call()
            http_url = token_uri.replace('ipfs://', 'https://gateway.pinata.cloud/ipfs/')
            
            # Fetch metadata from HTTP URL
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
=======
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

# Print all environment variables (be careful with sensitive data)
print("All environment variables loaded:", {k: v for k, v in os.environ.items() if 'PINATA' in k})

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with your secret key

# Initialize Web3
ALCHEMY_URL = os.getenv('ALCHEMY_URL')
web3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))
print("Connected to Sepolia via Alchemy")

# Contract details
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
CONTRACT_ABI =  [
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "approve",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "sender",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "ERC721IncorrectOwner",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "ERC721InsufficientApproval",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "approver",
				"type": "address"
			}
		],
		"name": "ERC721InvalidApprover",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			}
		],
		"name": "ERC721InvalidOperator",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "ERC721InvalidOwner",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "receiver",
				"type": "address"
			}
		],
		"name": "ERC721InvalidReceiver",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "sender",
				"type": "address"
			}
		],
		"name": "ERC721InvalidSender",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "ERC721NonexistentToken",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "recipient",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "logURI",
				"type": "string"
			}
		],
		"name": "mintDataLogNFT",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "OwnableInvalidOwner",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "OwnableUnauthorizedAccount",
		"type": "error"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "approved",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "Approval",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "bool",
				"name": "approved",
				"type": "bool"
			}
		],
		"name": "ApprovalForAll",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "_fromTokenId",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "_toTokenId",
				"type": "uint256"
			}
		],
		"name": "BatchMetadataUpdate",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "_tokenId",
				"type": "uint256"
			}
		],
		"name": "MetadataUpdate",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "previousOwner",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "OwnershipTransferred",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "renounceOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "safeTransferFrom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			},
			{
				"internalType": "bytes",
				"name": "data",
				"type": "bytes"
			}
		],
		"name": "safeTransferFrom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			},
			{
				"internalType": "bool",
				"name": "approved",
				"type": "bool"
			}
		],
		"name": "setApprovalForAll",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "Transfer",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "transferFrom",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "balanceOf",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "getApproved",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "getOwnedTokens",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "getTokenOwner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "operator",
				"type": "address"
			}
		],
		"name": "isApprovedForAll",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "name",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "nextTokenId",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "ownerOf",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes4",
				"name": "interfaceId",
				"type": "bytes4"
			}
		],
		"name": "supportsInterface",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "symbol",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "tokenId",
				"type": "uint256"
			}
		],
		"name": "tokenURI",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]  # Your contract ABI here
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Wallet details
wallet_address = os.getenv('WALLET_ADDRESS')
private_key = os.getenv('PRIVATE_KEY')

def upload_to_ipfs(metadata):
    try:
        url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
        
        # Use the loaded JWT token
        headers = {
            'Authorization': f'Bearer {os.getenv("PINATA_JWT")}',
            'Content-Type': 'application/json'
        }
        
        print("Attempting IPFS upload...")
        print(f"Metadata being uploaded: {metadata}")
        
        response = requests.post(
            url,
            headers=headers,
            json=metadata
        )
        
        print(f"Pinata response status: {response.status_code}")
        print(f"Pinata response: {response.text}")
        
        if response.status_code == 200:
            ipfs_hash = response.json()["IpfsHash"]
            print(f"Successfully uploaded to IPFS with hash: {ipfs_hash}")
            return f"ipfs://{ipfs_hash}"
        else:
            print(f"Error uploading to IPFS: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error in upload_to_ipfs: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect_wallet', methods=['POST'])
def connect_wallet():
    wallet_address = request.json.get('wallet_address')
    if wallet_address:
        session['wallet_address'] = wallet_address
        return jsonify({'message': 'Wallet connected successfully'})
    return jsonify({'error': 'No wallet address provided'}), 400

@app.route('/check_auth')
def check_auth():
    return jsonify({'authenticated': 'wallet_address' in session})

@app.route('/log_data', methods=['POST'])
def log_data():
    if 'wallet_address' not in session:
        return jsonify({'error': 'Please connect your wallet first'}), 401
        
    try:
        next_token_id = contract.functions.nextTokenId().call()
        
        description = request.form['description']
        # Convert datetime string to Unix timestamp
        timestamp_str = request.form['timestamp']
        timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M')
        timestamp = int(timestamp_dt.timestamp())
        
        # Create metadata with standard NFT metadata format
        metadata = {
            "name": f"Data Log NFT #{next_token_id}",
            "description": description,
            "image": "https://your-default-image-url.png",  # Add a default image URL
            "external_url": "",  # Optional: Add if you have a website
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
        
        # Upload to IPFS
        metadata_uri = upload_to_ipfs(metadata)
        if not metadata_uri:
            return jsonify({'error': 'Failed to upload metadata to IPFS'}), 500
        
        # Convert IPFS URI to HTTP URL for viewing
        ipfs_hash = metadata_uri.replace('ipfs://', '')
        http_url = f'https://gateway.pinata.cloud/ipfs/{ipfs_hash}'
        
        # Mint the NFT
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
            'view_url': http_url,
            'etherscan_url': f'https://sepolia.etherscan.io/tx/{tx_hash.hex()}'
        })
        
    except Exception as e:
        print(f"Error in log_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_nfts')
def get_nfts():
    if 'wallet_address' not in session:
        return jsonify({'error': 'Please connect your wallet first'}), 401
        
    try:
        user_address = to_checksum_address(session['wallet_address'])
        token_ids = contract.functions.getOwnedTokens(user_address).call()
        
        nfts = []
        for token_id in token_ids:
            token_uri = contract.functions.tokenURI(token_id).call()
            # Convert IPFS URI to HTTP URL
            http_url = token_uri.replace('ipfs://', 'https://gateway.pinata.cloud/ipfs/')
            nfts.append({
                "tokenId": token_id,
                "tokenURI": http_url
            })
            
        return jsonify({"nfts": nfts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search_by_id')
def search_by_id():
    try:
        search_id = request.args.get('id')
        if not search_id:
            return jsonify({'error': 'No ID provided'}), 400
            
        token_id = int(search_id)
        # Verify token exists and get its URI
        try:
            token_uri = contract.functions.tokenURI(token_id).call()
            # Convert IPFS URI to HTTP URL
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
            
        # Get all tokens owned by the user
        user_address = to_checksum_address(session['wallet_address'])
        token_ids = contract.functions.getOwnedTokens(user_address).call()
        
        matching_nfts = []
        for token_id in token_ids:
            token_uri = contract.functions.tokenURI(token_id).call()
            http_url = token_uri.replace('ipfs://', 'https://gateway.pinata.cloud/ipfs/')
            
            # Fetch metadata from HTTP URL
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
            
        # Convert search timestamp to Unix timestamp
        search_dt = datetime.strptime(search_timestamp, '%Y-%m-%dT%H:%M')
        search_unix = int(search_dt.timestamp())
        
        # Get all tokens owned by the user
        user_address = to_checksum_address(session['wallet_address'])
        token_ids = contract.functions.getOwnedTokens(user_address).call()
        
        matching_nfts = []
        for token_id in token_ids:
            token_uri = contract.functions.tokenURI(token_id).call()
            http_url = token_uri.replace('ipfs://', 'https://gateway.pinata.cloud/ipfs/')
            
            # Fetch metadata from HTTP URL
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
>>>>>>> 4e76b30bce46dd9625cc7a22ab65fc1507a6344f
    app.run(debug=True)