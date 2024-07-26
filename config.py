ServerName = "PyHTTP"       # Server name, used in Server header as well as on default error pages.
Port       = 7000           # Port to serve on, default is 7000
Bind       = "0.0.0.0"      # IP Address to bind to, default is 0.0.0.0. Use 127.0.0.1 to only allow local connections
WebRoot    = "webroot"      # Web server root directory, do not include the last / in the path
SSLEnable  = False          # HIGHLY UNSTABLE, DO NOT USE
CertPath   = "ssl/cert.pem" # Path to SSL Cert, requires SSLEnable
KeyPath    = "ssl/key.pem"  # Path to SSL Key, requires SSLEnable
SSLPort    = 7443           # Port to serve SSL on, default is 7443, requires SSLEnable

############################
# Extensions Configuration #
############################

# TODO: Extensions are a WIP and may not work, use with caution

# Extensions to run after loading the document.
ExtDoc = [
    
]

# Extensions that run after creating headers.
ExtHead = [
    
]