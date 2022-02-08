import web3
import os, sys
import logging

from contracts import repoABI, repoCode

logger = logging.getLogger(__name__)

def create(w3, account):
    logger.info('Creating new repository with administrator ' + account)
    w3.eth.contract(repoABI)(


if __name__ == '__main__':
    import argparse, sys

    def abort(msg):
        print(msg, file=sys.stderr)
        sys.exit(1)
    
    def validated_addr(addr):
        addr = str(addr)
        if not web3.isAddress(addr):
            raise TypeError('Invalid address')
        return addr

    parser = argparse.ArgumentParser()
    parser.add_argument('-R', '--repo', type=str, help='Repository address')
    parser.add_argument('--admin', type=bool, help='Treat as administrator')
    parser.add_argument('--account', type=validated_addr, default=w3.eth.defaultAccount, help='Sender account (a current administrator)')
    subparsers = parser.add_subparsers(required=True)
    create_parser = subparser.add_parser('create', description='Create repository')
    create_parser.set_defaults(func=create)
    status_parser = subparser.add_parser('status', description='Check status of repository')
    status_parser.set_defaults(func=status)
    obsolete_parser = subparser.add_parser('obsolete', description='Mark repository obsolete')
    obsolete_parser.set_defaults(func=obsolete)
    auth_parser = subparser.add_parser('authorize', description='Authorize account with write access')
    auth_parser.add_argument('address', type=str)
    auth_parser.set_defaults(func=authorize)
    deauth_parser = subparser.add_parser('deauthorize', description='Deauthorize account')
    deauth_parser.add_argument('address', type=str)
    deauth_parser.set_defaults(func=deauthorize)

    args = parser.parse_args()
    if not web3.isAddress(args.repo):
        abort('Invalid repository address')

    print('Initializing...', file=sys.stderr)

    # https://cloudflare-eth.com
    w3 = web3.Web3(Web3.HTTPProvider(os.environ['ETHEREUM_RPC_URL'] || 'http://localhost:8545'))
    if not w3.eth.defaultAccount:
        w3.eth.defaultAccount = w3.eth.coinbase

    args.func(args)
