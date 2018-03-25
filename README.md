# Radio-Canada-Hackathon2018
Backend lineup crawler for a Search bar on a Radio-Canada website, Radio-Canada API, Microsoft Text Analytics
  
The lineup_crawler is a script for news extraction from Radio-Canada API.

## Workflow 
The lineup_crawler is a script for news extraction from Radio-Canada API.
It works in a following way:
For each region_id script makes a request to Radio-Canada API and process returned JSON. Next, each extracted news summary is submitted to Microsoft text analytics API, that results in text sentiment rate and some key words. All that data is uploaded to MySQL DB afterwards.

## Submission
This script is a part of a final submission of the Radio-Canada Hackathon 2018.

Team GWAM. Its proud members are Irina Kim, Nikita Ponamaryov, Steve Gagné, Alexander Kim and Anton Pavlov.
March 2018
