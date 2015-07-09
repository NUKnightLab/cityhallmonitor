### Local development setup

#### 1.  Setup PostgreSQL

Download and run installer for Mac OS X Version 9.3.9

http://www.enterprisedb.com/products-services-training/pgdownload

    Default installation directory = /Library/PostgreSQL/9.3
    Default data directory /Library/PostgreSQL/9.3/data
    Default Port = 5432
    Use default locale
    
Add the PostgreSQL bin directory to your PATH environment variable:

`PATH=$PATH:/Library/PostgreSQL/9.3/bin`

You may need to add the PostgreSQL lib directory to your DYLD_FALLBACK_LIBRARY_PATH environment variable:

`DYLD_FALLBACK_LIBRARY_PATH=$DYLD_FALLBACK_LIBRARY_PATH:/Library/PostgreSQL/9.3/lib`


        
