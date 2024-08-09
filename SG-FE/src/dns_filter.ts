import { lookup as originalLookup } from 'dns';
import { promisify } from 'util';

const dns = {
    lookup: (domain: string, options: any, callback: any) => {
        // Your custom implementation
        originalLookup(domain, options, callback);
    }
};

// Adding the __promisify__ property
(dns.lookup as any).__promisify__ = promisify(dns.lookup);

export default dns;