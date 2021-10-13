# Himawari-8 Data Product Downloader

My customized class based on Curl to download data products of [JAXA Himawari-8](https://www.eorc.jaxa.jp/ptree/userguide.html). Currently only SWR (Short Wave Radiation) L2 product was tested.

## Environment

* Install Curl on the operation system and add to the path.
* Install required packages

```bash
pip install -r requirements.txt
```

## Use case

* Register a new account from [JAXA](https://www.eorc.jaxa.jp/ptree/registration_top.html).
* Download SWR data of a period to a local directory.

```python
from HimawariDownloader import HimawariDownloader
from datetime import datetime, timedelta

# set up start time and end time
start_time = datetime(2021, 5, 11, 3)
end_time = start_time + timedelta(hours=4)
print(start_time, end_time)

SWRDownloader = HimawariDownloader(
    user = 'email',    # replace with email address of the registered account
    pwd = 'password',  # replace with the password
    level = 'L2', 
    product = 'PAR', 
    version = '010', 
    local_root_dir = '/local/path',   # replace with a local path
)

start_time_utc, end_time_utc = start_time - timedelta(hours=8), end_time - timedelta(hours=8)
SWRDownloader.download_period(start_time_utc, end_time_utc)
```
