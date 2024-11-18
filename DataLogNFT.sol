// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract DataLogNFT is ERC721URIStorage, Ownable {
    uint256 public nextTokenId = 1;
    mapping(address => uint256[]) private ownerTokens;
    mapping(uint256 => address) private tokenOwners;

    constructor() ERC721("DataLogNFT", "DLNFT") Ownable(msg.sender)  {}

    function mintDataLogNFT(address recipient, string memory logURI) external onlyOwner {
        _safeMint(recipient, nextTokenId);
        _setTokenURI(nextTokenId, logURI);
        
        // Track ownership without Enumerable
        ownerTokens[recipient].push(nextTokenId);
        tokenOwners[nextTokenId] = recipient;

        nextTokenId++;
    }

    function getOwnedTokens(address owner) external view returns (uint256[] memory) {
        return ownerTokens[owner];
    }

    function getTokenOwner(uint256 tokenId) external view returns (address) {
        return tokenOwners[tokenId];
    }
}
