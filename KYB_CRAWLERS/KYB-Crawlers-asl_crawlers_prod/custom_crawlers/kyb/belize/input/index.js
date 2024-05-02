import fetch from 'node-fetch';
import fs from 'fs'
import puppeteer from 'puppeteer';
import { exit } from 'process';

const CSV_PATH = 'belize/input/belize-data.csv'
const browser = await puppeteer.launch({headless:"new",args: ['--no-sandbox']});
const [page] = await browser.pages();
var HEADERS = null;
page.on('request', interceptedRequest => {
  if (interceptedRequest.isInterceptResolutionHandled()) return;
  if(interceptedRequest.url().includes('business.json')){
      HEADERS = interceptedRequest.headers()
  }
});
await page.goto('https://obrs.bccar.bz/bereg/searchbusinesspublic');
await page.setDefaultTimeout(3000)
const COOKIES = (await page.cookies()).map((cookie) => { return `${cookie.name}=${cookie.value}`; }).join('; ');
await browser.close()
const res = await fetch("https://obrs.bccar.bz/bereg/list/public/business.json", {
  "headers": {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "content-type": "application/json",
    "ncsrf": HEADERS['ncsrf'],
    "sec-ch-ua": "\"Chromium\";v=\"104\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"104\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "cookie": COOKIES,
    "Referer": "https://obrs.bccar.bz/bereg/searchbusinesspublic",
    "Referrer-Policy": "strict-origin-when-cross-origin"
  },
  "body": "{\"PageSize\":10,\"PageNumber\":1}",
  "method": "POST"
}).then((res)=>res.json())

const map = res['Map']
const row = map.join(',')

if(fs.existsSync(CSV_PATH))
  fs.unlinkSync(CSV_PATH)

fs.writeFileSync(CSV_PATH, `${row}\n`,  {flag: 'a+' })

const TOTAL_RECORDS = res['TotalRecordCount']
const PER_PAGE = 700;
const TOTAL_PAGES = Math.ceil(TOTAL_RECORDS / PER_PAGE)

for(let i = 1; i<=TOTAL_PAGES; i++) {
    console.log(`crawling page: ${i}`)
    const data = await fetch("https://obrs.bccar.bz/bereg/list/public/business.json", {
                    "headers": {
                      "accept": "application/json, text/javascript, */*; q=0.01",
                      "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
                      "content-type": "application/json",
                      "ncsrf": HEADERS['ncsrf'],
                      "sec-ch-ua": "\"Chromium\";v=\"104\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"104\"",
                      "sec-ch-ua-mobile": "?0",
                      "sec-ch-ua-platform": "\"macOS\"",
                      "sec-fetch-dest": "empty",
                      "sec-fetch-mode": "cors",
                      "sec-fetch-site": "same-origin",
                      "x-requested-with": "XMLHttpRequest",
                      "cookie": COOKIES,
                      "Referer": "https://obrs.bccar.bz/bereg/searchbusinesspublic",
                      "Referrer-Policy": "strict-origin-when-cross-origin"
                    },
                    "body": `{\"PageSize\":${PER_PAGE},\"PageNumber\":${i}}`,
                    "method": "POST"
                    }).then((res)=>res.json())
    const records = data['Records']
    for(let record of records){
        record = record.map((e)=>`"${e?e.replaceAll('"',''):e}"`)
        const row = record.join(',')
        fs.writeFileSync(CSV_PATH, `${row}\n`,  {flag: 'a+' })
    }
}
console.log('FINISHED')
exit(0)