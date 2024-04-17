import argparse, uuid, boto3, sys, time
from datetime import datetime,timedelta

def create_cloudfront_distribution(origin_domain_name):
    client = boto3.client('cloudfront')

    distribution_config = {
        'CallerReference': str(uuid.uuid4()), 
        'Comment': 'CDN for ' + origin_domain_name,
        'Aliases': {
        'Quantity': 0
        }, 
        'DefaultRootObject': '',
            'Origins': {
                'Quantity': 1, 'Items': [
                    {
                        'Id': origin_domain_name, 
                        'DomainName': origin_domain_name, 
                        'OriginPath': '', 
                        'CustomHeaders': {
                        'Quantity': 0
                        }, 
                        'CustomOriginConfig': {
                            'HTTPPort': 80, 
                            'HTTPSPort': 443, 
                            'OriginProtocolPolicy': 'match-viewer', 
                            'OriginSslProtocols': {
                                'Quantity': 1, 
                                'Items': [
                                    'TLSv1.2'
                                ]
                            }, 
                            'OriginReadTimeout': 30, 
                            'OriginKeepaliveTimeout': 5
                        }, 
                        'ConnectionAttempts': 3, 
                        'ConnectionTimeout': 10, 
                        'OriginShield': {
                            'Enabled': False
                        }, 
                        'OriginAccessControlId': ''
                    }
                ]
            }, 
            'OriginGroups': {
                'Quantity': 0
            }, 
            'DefaultCacheBehavior': {
                'TargetOriginId': origin_domain_name, 
                'TrustedSigners': {
                    'Enabled': False, 
                    'Quantity': 0
                }, 
                'TrustedKeyGroups': {
                    'Enabled': False, 
                    'Quantity': 0
                }, 
                'ViewerProtocolPolicy': 'allow-all', 
                'AllowedMethods': {
                    'Quantity': 7, 
                    'Items': [
                        'HEAD', 'DELETE', 'POST', 'GET', 'OPTIONS', 'PUT', 'PATCH'
                    ], 
                    'CachedMethods': { # GET and HEAD are cached by default, this cannot be turned off, but later configured in cache settings
                        'Quantity': 2, 
                        'Items': [
                            'HEAD', 'GET'
                        ]
                    }
                }, 
                'SmoothStreaming': False, 
                'Compress': False, 
                'LambdaFunctionAssociations': {
                    'Quantity': 0
                }, 
                'FunctionAssociations': {
                    'Quantity': 0
                }, 
                'FieldLevelEncryptionId': '', 
                'ForwardedValues': {
                    'QueryString': False, 
                    'Cookies': {
                        'Forward': 'none'
                    }, 
                    'Headers': {
                        'Quantity': 0
                    }, 
                    'QueryStringCacheKeys': {
                        'Quantity': 0
                    }
                }, 
                'MinTTL': 0, 
                'DefaultTTL': 86400, 
                'MaxTTL': 31536000
            }, 
            'CacheBehaviors': {
                'Quantity': 0
            }, 
            'CustomErrorResponses': {
                'Quantity': 0
            }, 
            'Comment': '', 
            'Logging': {
                'Enabled': False, 
                'IncludeCookies': False, 
                'Bucket': '', 
                'Prefix': ''
            }, 
            'PriceClass': 'PriceClass_100', 
            'Enabled': True, 
            'ViewerCertificate': {
                'CloudFrontDefaultCertificate': True, 
                'SSLSupportMethod': 'vip', 
                'MinimumProtocolVersion': 'TLSv1', 
                'CertificateSource': 'cloudfront'
            }, 
            'Restrictions': {
                'GeoRestriction': {
                    'RestrictionType': 'none', 
                    'Quantity': 0
                }
            }, 
            'WebACLId': '', 
            'HttpVersion': 'http2', 
            'IsIPV6Enabled': False, 
            'ContinuousDeploymentPolicyId': '', 
            'Staging': False}

    response = client.create_distribution(DistributionConfig=distribution_config)
    get_cloudfront_domainName(response['Distribution']['Id'])
    return response['Distribution']['Id']


def delete_cloudfront_distribution(distribution_id):
    client = boto3.client('cloudfront')
    resp = client.get_distribution_config(Id=distribution_id)
    resp['DistributionConfig']['Enabled'] = False

    result = client.update_distribution(
        DistributionConfig=resp['DistributionConfig'], 
        Id=distribution_id, 
        IfMatch=client.get_distribution(Id=distribution_id)['ETag'])

    #wait for distribution to disable....
    print("Waiting while the distribution is disabled. This may take several minutes.")
    timeout_mins=15 
    wait_until = datetime.now() + timedelta(minutes=timeout_mins)
    notFinished=True
    eTag=""
    while(notFinished):
        #check for timeout
        if wait_until < datetime.now():
            #timeout
            print("Distribution took too long to disable. Exiting")
            sys.exit(1)

        status=client.get_distribution(Id=distribution_id)
        if(status['Distribution']['DistributionConfig']['Enabled']==False and status['Distribution']['Status']=='Deployed'):
            eTag=status['ETag']
            notFinished=False

        print("Not completed yet. Sleeping 60 seconds....")
        time.sleep(60) 

    #delete distribution
    client.delete_distribution(Id=distribution_id, IfMatch=eTag)  


def get_cloudfront_distribution_config(distribution_id):
    client = boto3.client('cloudfront')
    response = client.get_distribution_config(Id=distribution_id)
    get_cloudfront_domainName(distribution_id)
    return response['DistributionConfig']


def get_cloudfront_domainName(distribution_id):
    client = boto3.client('cloudfront')
    domainName = client.get_distribution(Id=distribution_id)["Distribution"]["DomainName"]
    print(domainName)


def main():
    parser = argparse.ArgumentParser(description="Create and delete C2 Front Ends")
    # parser.add_argument("domain_name", type=str, help="Domain name for the CDN")
    parser.add_argument("-c", "--create", help="Create CloudFront CDN Distribution", action="store_true")
    parser.add_argument("-r", "--read", help="Get existing CDN config", action="store_true")
    parser.add_argument("-d", "--delete", help="Existing CDN Distribution ID", action="store_true")
    parser.add_argument("-o", "--origin", type=str, help="Origin server domain name")
    parser.add_argument("-i", "--id", type=str, help="Existing CDN Distribution ID")
    args = parser.parse_args()

    if args.create:
        distribution_id = create_cloudfront_distribution(args.origin)
        print("CloudFront Distribution ID:", distribution_id)
    elif args.read:
        distribution_config = get_cloudfront_distribution_config(args.id)
        print(distribution_config)
    elif args.delete:
        response = delete_cloudfront_distribution(args.id)
        print("CloudFront Distribution Deleted " + str(response))


if __name__ == "__main__":
    main()
