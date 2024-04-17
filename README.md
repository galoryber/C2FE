# C2FE
C2 Front End - a tool to quickly add various front end domains to your C2 infrastructure

### Example

You have your C2 Server
You have your proxy / redirector

but those use some DNS domain right now... 

Avoid Domain name categorization issues and deploy multiple front end options that point back to clearly-evil.example.com

## Usage 
``` 
usage: C2FE.py [-h] [-c] [-r] [-d] [-o ORIGIN] [-i ID]

Create and delete C2 Front Ends

options:
  -h, --help            show this help message and exit
  -c, --create          Create CloudFront CDN Distribution
  -r, --read            Get existing CDN config
  -d, --delete          Existing CDN Distribution ID
  -o ORIGIN, --origin ORIGIN
                        Origin server domain name
  -i ID, --id ID        Existing CDN Distribution ID
```

# ToDo
- Add -t --type flag for various options like: Cloudfront, Azure FrontDoor, etc
- research types: AWS API Gateway, MS Dev Tunnels, Cloudflare tunnels, more
