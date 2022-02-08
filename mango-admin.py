#!/usr/bin/env python3
import os, sys
import logging

from contracts import repoABI, repoCode

logger = logging.getLogger(__name__)

def create(w3):
    logger.info('Creating new repository with administrator ' + str(w3.eth.default_account))
    ct = w3.eth.contract(abi=repoABI, bytecode=repoCode)
    constructor = ct.constructor()
    transactionHash = constructor.transact()
    logger.info('Sent transaction: ' + transactionHash)
    address = w3.eth.get_transaction_receipt(transactionHash)['contractAddress']
    logger.info('Repository created: ' + address)
    logger.warn("Don't forget to verify the contract tx is confirmed on-chain!")

    return address

def status(w3, repo):
    logger.info('Checking status of repository ' + repo)
    
    ct = w3.eth.contract(address=repo, abi=repoABI)
    version = ct.functions.repoInterfaceVersion().call()
    if version != 1:
        raise TypeError('Not a Mango repository')

    if ct.isObsolete():
        logger.warn('Repository is marked as OBSOLETE')


    refnames = [ ct.functions.refName(i).call() for i in range(ct.functions.refCount().call()) ]
    if len(refnames) == 0:
        logger.warn('No references')
    refs = { name : ct.getRef(name) for name in refnames }

    for name, ref in refs.items():
        logger.info('Reference: ' + name + ' -> ' + ref)

    snapshots = [ct.functions.getSnapshot(i).call() for i in range(ct.functions.snapshotCount().call())]
    if len(snapshots) == 0:
        logger.info('No snapshots')
    
    for idx, snapshot in enumerate(snapshots):
        logger.info('Snapshot #' + str(i) + ': ' + snapshot)

    return refs, snapshots

def obsolete(w3, repo):
    logger.info('Marking ' + repo + ' as obsolete')

    ct = w3.eth.contract(address=repo, abi=repoABI)
    transactionHash = ct.functions.setObsolete().call().transact()
    logger.info('Sent transaction: ' + transactionHash)
    logger.warn("Don't forget to verify the tx is confirmed on-chain!")
    
    return transactionHash

def authorize(w3, repo, address, admin = False):
    logger.info('Authorizing ' + address + ' for ' + repo + ' as ' + ('committer', 'admin')[admin])

    ct = w3.eth.contract(address=repo, abi=repoABI)
    transactionHash = ct.functions.authorize(address, admin).transact()
    logger.info('Sent transaction: ' + transactionHash)
    logger.warn("Don't forget to verify the tx is confirmed on-chain!")

    return transactionHash

def deauthorize(w3, repo, address, admin = True):
    logger.info('Deauthorizing ' + address + ' for ' + repo + ' as ' + ('committer', 'admin')[admin])

    ct = w3.eth.contract(address=repo, abi=repoABI)
    transactionHash = ct.functions.deauthorize(address, admin).transact()
    logger.info('Sent transaction: ' + transactionHash)
    logger.warn("Don't forget to verify the tx is confirmed on-chain!")

    return transactionHash



if __name__ == '__main__':
    import argparse, sys

    def abort(msg):
        print(msg, file=sys.stderr)
        sys.exit(1)
    
    def validated_addr(addr):
        addr = str(addr)
        import web3
        if not web3.isAddress(addr):
            raise TypeError('Invalid address')
        return addr

    parser = argparse.ArgumentParser()
    parser.add_argument('--account', type=validated_addr, help='Sender account (a current administrator)')
    subparsers = parser.add_subparsers(required=True)
    create_parser = subparsers.add_parser('create', description='Create repository')
    create_parser.set_defaults(func=create)
    status_parser = subparsers.add_parser('status', description='Check status of repository')
    status_parser.add_argument('-R', '--repo', type=validated_addr, required=True, help='Repository address')
    status_parser.set_defaults(func=status)
    obsolete_parser = subparsers.add_parser('obsolete', description='Mark repository obsolete')
    obsolete_parser.add_argument('-R', '--repo', type=validated_addr, required=True, help='Repository address')
    obsolete_parser.set_defaults(func=obsolete)
    auth_parser = subparsers.add_parser('authorize', description='Authorize account with write access')
    auth_parser.add_argument('-R', '--repo', type=validated_addr, required=True, help='Repository address')
    auth_parser.add_argument('address', type=str)
    auth_parser.add_argument('--admin', type=bool, help='Treat as administrator')
    auth_parser.set_defaults(func=authorize)
    deauth_parser = subparsers.add_parser('deauthorize', description='Deauthorize account')
    deauth_parser.add_argument('-R', '--repo', type=validated_addr, required=True, help='Repository address')
    deauth_parser.add_argument('address', type=str)
    deauth_parser.add_argument('--admin', type=bool, help='Treat as administrator')
    deauth_parser.set_defaults(func=deauthorize)

    args = parser.parse_args()

    print('Initializing...', file=sys.stderr)

    import web3

    # https://cloudflare-eth.com
    w3 = web3.Web3(web3.Web3.HTTPProvider(os.environ.get('ETHEREUM_RPC_URL') or 'http://localhost:8545'))
    while True:
        try:
            if w3.isConnected():
                break
        except Exception:
            pass
        print('not connected yet, waiting ...')
        import time
        time.sleep(0.5)

    account = args.__dict__.pop('account')
    func = args.__dict__.pop('func')
    if account is None:
        if not w3.eth.default_account:
            try:
                w3.eth.default_account = w3.eth.coinbase
            except:
                pass
    else:
        w3.eth.default_account = account
    func(w3, **args.__dict__)
