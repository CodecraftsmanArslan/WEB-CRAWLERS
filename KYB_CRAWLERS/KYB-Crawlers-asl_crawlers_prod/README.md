
# KYB- Manual Crawlers

  
<br>

  

## Table of Contents

  

<summary>Table of Contents</summary>

<br>

<ol>

<li><a  href="#KYB-Manual-Crawlers">KYB Manual Crawlers</a></li>
<li><a  href="#Crawler-Workflow">Crawler Workflow</a></li>
<li><a  href="#crawler-details">Crawler Details</a>
<ul>

<li>
<a  href="#stack-used">Stack Used</a></li>

<li>  <a  href="#installation-procedure">Installation Procedure</a>  </li>

<li>  <a  href="#directory-structure">Directory Structure</a>  </li>

<li>  <a  href="#crawlers-directory-structure">Crawlers Directory Structure</a> </li>
<li>  <a   href="#third-party-integrations">Third Party Integrations</a></li>
<ul>

<li>  <a  href="#Crawlers_v2/official_registries">Crawlers_v2/official_registries</a>  </li>
<li>  <a  href="#custom-crawlers">Custom Crawlers</a>  </li>
<li> <a href="#db-scripts">DB Scripts</a>  </li>
<li>  <a  href="#helpers">Helpers</a>  </li>
<li>  <a  href="#translation-scripts">Translation Scripts</a>  </li>
</ul>

</ul>

</li>

</ol>

<br>

#

# KYB Manual Crawlers :

The manual crawling module is specifically crafted to adeptly handle both structured and unstructured data across various formats, including HTML, PDF, CSV, and JSON-APIs. The module excels at extracting information from the designated data sources, seamlessly mapping the acquired data to predefined keys outlined in the key mapping document.  
Upon successful extraction and mapping, the module intelligently transforms the data into a structured JSON object. This refined JSON object is then efficiently stored in a Postgres-DB, ensuring data integrity and accessibility.

  

<hr>

## Crawler Workflow
<img src="workflow/workflow.png " title="Crawlers workflow">
 

## Crawler Details

  

<details  open>

<summary>Crawler Details</summary>

<br>

<ol>

### Stack Used

  

- [Python (Crawler Scripts)](https://www.python.org/)

- [Postgresql (Database)](https://www.postgresql.org/)

  

## Installation Procedure

  

### Manual Installation

  

### Installation Steps

  

<div  id="installation"><div>

  

1. Clone the repository from git and `cd` into it. <br  />

  

```

git clone https://github.com/Enlatics/KYB-Crawlers.git

```

  

2. Install the required packages with <br  />

  

```

pip install -r requirements.txt

```

3. Copy .env.example to .env

  

```

cp .env.example .env

```

 

4. In the .env file update database credentials


5. Install a custom crawler package 
```
pip install helpers/custom_crawler/dist/custom_crawler-1.0.tar.gz
```
  
#

### Directory Structure

```

root

|--crawlers_v2/official_registries (contains optimized manual crawlers)

|--custom_crawlers (contains all manual crawlers)

|--db_scripts (DB slack notification for all records)

|--helpers (contains all helpers functions)

|--translation_scripts (contains translation_scripts)

```
## Third Party Integrations


### External Packages

The following external packages are used:

1. [NopeCHA](https://pypi.org/project/nopecha/) (This package is used to resolve Captcha on website.)
2. [Webshare](https://www.webshare.io/homepage) (IP proxies of webshare are also used for IP switching.)
3. [Undetected-Chromedriver](https://pypi.org/project/undetected-chromedriver/)(This packahge is used to resolve CloudFlare Captcha by passing proxy as well.)

<hr>

# Crawlers Directory Structure
<ol>
<li>

## Crawlers_v2/official_registries
</li>
Within this directory, you'll find a collection of optimized crawlers that have been enhanced with multiprocessing and multithreading capabilities. Additionally, we've implemented an improved resume functionality to seamlessly execute tasks across multiple screens on the server, enhancing the speed at which data can be retrieved and reviewed.  

<strong>Resume functionality:</strong> Enhance your crawler's efficiency by specifying starting and ending parameters, providing a customizable and targeted data extraction experience.

<hr>


### Directory Structure

```
root
|-- crawlers_v2/official_registries
	|-- source.py (Script that contains the logic of data extraction)
```
<hr>

<li>

## Custom Crawlers
</li>

In this directory, you'll discover crawlers designed for different categories:
<li> Insolvency </li>
<li> International </li>
<li> KYB Official Registry </li>


<hr>

### Directory Structure

```
root
|--custom_crawlers
	|--insolvency
		|-- source.py (Script that contains logic of data extraction)
	|--international
		|-- source.py (Script that contains logic of data extraction)
	|--kyb (Official Registry)
		|-- source.py (Script that contains logic of data extraction)
```

#

## DB Scripts

Our streamlined database script sends Slack notifications twice daily at 9:30 am and 6:30 pm. It provides essential details including country names, total records, sync status (Synced/Not Synced), and QA Approval/Unapproval counts. Keeping the team informed effortlessly.


### Directory Structure

```
root
|--db_scripts
	|--db_stats_staging.py
```


## Helpers

The "helpers" directory houses essential functions utilized in our custom crawlers. To streamline the integration of these functions into various crawlers, we have developed a Python package named **custom_crawler-1.0.tar.gz**. You can find this package conveniently located in the "dist" directory, ready for seamless incorporation into your projects.

<hr>

### Directory Structure

```
root
|--helpers
	|--custom_crawler
		|--dist
			|--custom_crawler-1.0.tar.gz
		|--CustomCrawler.py
		|--DBHelper.py 
		|--LoggerKYB.py
		|--request_helper.py
		|--proxies_list.py
		|--object_prepare.py
		|--selenium_helper.py
		|--SlackNotifyKYB.py
		|--setup.py
	
```
<hr>
For more details:

1.  <a href="https://github.com/Enlatics/KYB-Crawlers/blob/asl_crawlers_prod/helpers/custom_crawler/CustomCrawler.py"><strong>CustomCrawler.py:</strong> </a>
    
    -   This is the core module orchestrating the custom crawler, serving as the central component that ties together various functionalities.
2. <a href="https://github.com/Enlatics/KYB-Crawlers/blob/asl_crawlers_prod/helpers/custom_crawler/DBHelper.py"><strong>DBHelper.py:</strong> </a>
    
    -   Contains functions related to database interactions, ensuring seamless integration with database operations in the crawler.
3. <a href="https://github.com/Enlatics/KYB-Crawlers/blob/asl_crawlers_prod/helpers/custom_crawler/LoggerKYB.py"><strong>LoggerKYB.py:</strong> </a>

    -   Manages logging functionalities for the custom crawler, facilitating efficient tracking and debugging of the crawling process.
    
4.  <a href="https://github.com/Enlatics/KYB-Crawlers/blob/asl_crawlers_prod/helpers/custom_crawler/request_helper.py"><strong>request_helper.py:</strong> </a>

    
    -   Offers essential tools for handling HTTP requests, streamlining the process of fetching data from web sources.
5.  <a href="https://github.com/Enlatics/KYB-Crawlers/blob/asl_crawlers_prod/helpers/custom_crawler/proxies_list.py"><strong>proxies_list.py:</strong> </a>

    
    -   Provides a list of proxies to enhance the crawler's ability to navigate through different web environments securely.
6.  <a href="https://github.com/Enlatics/KYB-Crawlers/blob/asl_crawlers_prod/helpers/custom_crawler/object_prepare.py"><strong>object_prepare.py:</strong> </a>

    
    -   Prepares and structures objects to be used within the custom crawler, ensuring a well-organized and efficient data processing flow.
7. <a href="https://github.com/Enlatics/KYB-Crawlers/blob/asl_crawlers_prod/helpers/custom_crawler/selenium_helper.py"><strong>selenium_helper.py:</strong> </a>
 
    
    -   Contains functions and tools tailored for Selenium-based interactions, enabling the crawler to navigate dynamic web pages effectively.
8.  <a href="https://github.com/Enlatics/KYB-Crawlers/blob/asl_crawlers_prod/helpers/custom_crawler/SlackNotifyKYB.py"><strong>SlackNotifyKYB.py:</strong> </a>

    
    -   Integrates Slack notification functionalities, allowing for real-time alerts and updates during the crawling process.
9.  <a href="https://github.com/Enlatics/KYB-Crawlers/blob/asl_crawlers_prod/helpers/custom_crawler/setup.py"><strong>setup.py:</strong> </a>

    
    -   This module is crucial for packaging and distribution. It assists in the installation and setup of the **custom_crawler-1.0.tar.gz** package, ensuring easy integration into external projects.


If you need to make any modifications to the package, simply apply the changes and include them in the package using the following command:

```
python3 custom_crawler/setup.py sdist
```

Executing this command ensures that any updates or adjustments are seamlessly integrated into the package, ensuring its continued effectiveness.
<hr>


</div>

## Translation Scripts

Within this directory, we house a translation script designed to seamlessly convert content from the native language into English. To facilitate this process, we employ a dedicated **translation_reports** table. Upon the initial entry of records in the native language, they are stored within this table. Subsequently, we systematically arrange and store the translations in ascending and descending order within the **reports** table, ensuring a comprehensive and organized overview of the translated content.

### Directory Structure

```
root
|--translation_scripts
	|--dump_translated_data.py
	|--dump_translated_data2.py
	|--dump_translated_updated.py
	
```
For more details:

1. <a href="https://github.com/Enlatics/KYB-Crawlers/blob/asl_crawlers_prod/translation_scripts/dump_translated_data.py"><strong>dump_translated_data.py:</strong> </a>

	- Script to translate records in ascending order.
2. <a href="https://github.com/Enlatics/KYB-Crawlers/blob/asl_crawlers_prod/translation_scripts/dump_translated_data_2.py"><strong>dump_translated_data2.py:</strong> </a>
	
	- Script to translate records in descending order.
3. <a href="https://github.com/Enlatics/KYB-Crawlers/blob/asl_crawlers_prod/translation_scripts/dump_translated_updated.py"><strong>dump_translated_updated.py:</strong> </a>
	
	- Script containing updated requirements for translation. Can be used as a reference for translation.

</details>
