# SSL Self-Signed Certificate Quickstart

In order to deploy the SDC/SDW, you will need to acquire an SSL/TLS certificate
for encyrpting HTTPS traffic. You can purchase these certificates from a number
of Certificate Authorities ("CA"s). However, for internal testing purposes, you
can produce self-signed certificates which will need to be manually trusted by
your browser.

**Step 1** Create Certificate Request File

The first step is to create a request file, with examples shown below for a
fictional company "Example Company LLC", based in New York, NY. The first
example is for a cluster which is accessed by direct IP (192.168.1.1), while the
second is for a cluster accessed via a hostname (my.local.cluster).

```
# Example req.conf (for local cluster accessed via IP)
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no
[req_distinguished_name]
C = US
ST = NY
L = New York
O = Example Company LLC
OU = Operations
CN = 192.168.1.1
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
[alt_names]
IP.1 = 192.168.1.1
```

```
# Example req.conf (for local cluster accessed via DNS)
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no
[req_distinguished_name]
C = US
ST = NY
L = New York
O = Example Company LLC
OU = Operations
CN = my.local.cluster
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
[alt_names]
DNS.1 = my.local.cluster
```

**Step 2** Set up variables

This step is not technically necessary, but may save you some typing.

```bash
# Set the name of the request file, examples above
SELF_SIGNED_REQUEST=req.conf
# Set your preferred key type, rsa:4096 is a 4096-bit RSA key
SELF_SIGNED_KEY_TYPE=rsa:4096
# Set the file to store your new key in
SELF_SIGNED_KEY=my-self-signed-cert-key.pem
# Set the file to store your new cert in
SELF_SIGNED_CERT=my-self-signed-cert.pem 
# Set the file to store the PKCS12 intermediate keystore in
SELF_SIGNED_INTERMEDIATE_KEYSTORE=my-self-signed-cert.pkcs12
# Set the file to store the JKS keystore in
SELF_SIGNED_JAVA_KEYSTORE=my-self-signed-cert.jks
```

**Step 3** Generate key and certificate in PEM format

This step will ask you for a password to encrypt your key file, if you set one,
keep track of it for the next step. Please note that this command will generate
a certificate that is valid for 1 year.

```bash
openssl req \
    -x509 \
    -config $SELF_SIGNED_REQUEST \
    -newkey $SELF_SIGNED_KEY_TYPE \
    -keyout $SELF_SIGNED_KEY \
    -out $SELF_SIGNED_CERT \
    -days 365
```

**Step 4** Generate intermediate keystore

The application server used in the SDC/SDW requires certificates to be provided
in the Java Key Store (JKS) format. Before that file can be produced, we must
first create a key store in the PKCS12 format. This command will prompt you for
the password you used in step 3, as well as a new password. You may re-use this
password at your discretion.

```bash
openssl pkcs12 \
    -export \
    -inkey $SELF_SIGNED_KEY \
    -in $SELF_SIGNED_CERT \
    -out $SELF_SIGNED_INTERMEDIATE_KEYSTORE
```

**Step 5** Generate Java Key Store

The final step produces the JKS file needed by the SDC/SDW. Again, this command
will prompt you for the password you set in step 4, as well as a new password.
Once again, you may re-use this password at your discretion. The password set
as well as the JKS file produced in this step will be the secrets you provide to
kubernetes.

```bash
keytool \
    -importkeystore \
    -trustcacerts \
    -srckeystore $SELF_SIGNED_INTERMEDIATE_KEYSTORE \
    -srcstoretype PKCS12 \
    -destkeystore $SELF_SIGNED_JAVA_KEYSTORE
```