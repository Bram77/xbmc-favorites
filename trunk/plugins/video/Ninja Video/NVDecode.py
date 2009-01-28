import binascii,sys
from Crypto.Cipher import AES

def decode(data):
    IV   = "6543209487240596"
    key  = 'd74Kv9duE8bk3Jh2'
    obj=AES.new(key,AES.MODE_CFB, IV)
    return obj.decrypt(binascii.unhexlify(data))


#ciph=decode('f73d263fb30a157c537fb8892c028d388bfb4c64ebdcab93531a723ef282558bfd65b243a614adbefaa11b9000d53cbf18b9de762ec86f3da4fd830022932ceadf53a380d625fe9ceadd36775da184966fd66f36158957cb09a8c8dc28664d002a9a549efb82096eb5316059791893a3862312d521770e0ecf5fd927374acf90c924bfec4b16fa6ab0ce')
#print ciph
