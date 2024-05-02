const puppeteer = require("puppeteer-extra"); 
const pluginStealth = require("puppeteer-extra-plugin-stealth"); 
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));
//save to executable path
const { executablePath } = require("puppeteer"); 
const fs = require('fs');
const { Configuration, NopeCHAApi } = require('nopecha');
// Use stealth 
puppeteer.use(pluginStealth());
const querystring = require('node:querystring');
const process  = require('node:process');

const args = [
  '--no-sandbox',
  '--disable-setuid-sandbox',
  '--start-maximized','--disable-dev-shm-usage',
  '--disable-web-security',
  '--disable-features=IsolateOrigins,site-per-process',
  // '--shm-size=3gb'
]
var argv = process.argv.slice(2);

// Nopecha configurations
const configuration = new Configuration({
  apiKey: 'sub_1NDMQECRwBwvt6pthcY5VBHp',
});
const nopecha = new NopeCHAApi(configuration);

const configuration1 = new Configuration({
  apiKey: 'sub_1NDMOICRwBwvt6ptRRsxMdmU',
});
const nopecha1= new NopeCHAApi(configuration1);

async function resolve_captcha(page) {
  var captcha_solved = false
  while(!captcha_solved) {
        console.log('resolving captcha')
        const img_base64 = await page.evaluate(()=>{
          const imgs = document.getElementsByTagName('img')
          return imgs[0].getAttribute('src')
        })
        var text = null;
        try{
           text = await nopecha.solveRecognition({
            type: 'textcaptcha',
            image_urls: [img_base64.split(',')[1]],
          });
        }catch(e){
          try{
            text = await nopecha1.solveRecognition({
             type: 'textcaptcha',
             image_urls: [img_base64.split(',')[1]],
           });
          }catch(e){
            try{
                const res = await fetch('http://127.0.0.1:5000/process',
                        {
                          method:'POST',
                          body: JSON.stringify({img: img_base64}),
                          headers: {'Content-Type': 'application/json'}
                        }  
                ).then((res)=>res.json())
                text = res['result']
              }catch(e){
                continue
              }
          }
        }
        if(!text){
          console.log('Null captcha text found continuting..')
          continue
        }
        // console.log(`captcha text: ${text}`)
        const element = await page.waitForSelector('#ans');
        element.focus()
        // const value = `${res['result']}`
        await page.evaluate((value) => {
          const el = document.getElementById('ans');
          el.value = value;
        },text);
        await page.evaluate(() => {
          const el = document.getElementById('jar');
          el.click();
        })
        // await delay(50000)
        // console.log('waiting for navigation')
        try{
          await page.waitForNavigation({timeout: 600000})
        }catch(e){
          continue
        }
        // console.log('after navigation')
        if((await page.content()).includes('You have entered an invalid answer for the question')){
          console.log('Found captcha: resolving')
          captcha_solved = false;
          // await delay()
        }else{
          captcha_solved = true;
          console.log('Captcha solved')
        }
  }
  return new Promise((r)=>r(true))
}


function delay(time) {
  return new Promise(function(resolve) { 
      setTimeout(resolve, time)
  });
}

// / Launch puppеteer-stealth 
puppeteer.launch({headless:'new', executablePath: executablePath(), args:args , defaultViewPort:null}).then(async browser => { 
	// Create a new page 
    const BASE_URL = "https://wyobiz.wyo.gov/Business/"
    const ENTRY_URL = "https://wyobiz.wyo.gov/Business/FilingSearch.aspx#&&h1ZxfKIYtVW80UdhX2eZ9dOt5AIUsTTulS7TJe694nljCtc8qzzhzjhjtLzRlodc2kVRpyMRzy0SZ5jx4RCPCH60e5xzeEwKe+mZ3LOHYE3GjTyxPncXYtND05fbI3Ziz1aLEjrh5gjG0AaFofGcT/XvL+QvzM4OyjAFkGBUBM8rSNUj"
    const page = (await browser.pages())[0]
    
    // await page.setRequestInterception(true)
    // REQUEST_INT = -1;
    // page.on('request',async(request)=>{    
    //     if (request.url().includes('Business/FilingSearch.aspx') && request.method() === 'POST' && REQUEST_INT<0){
    //     }
    //     request.continue()
    // })
    // page.on('response', async(response) => {
    //     const request = response.request();
    // })
  while(true){
    try{
      await page.goto(ENTRY_URL),{timeout: 60000};
      break
    }catch(e){}
  }

  if((await page.content()).includes('This question is for testing whether you are a human visitor and to prevent automated spam submission.')){
    console.log('Found captcha: resolving')
    resolve_captcha(page)
    
  } else {
    var next_page_el = await page.waitForSelector('#MainContent_lbtnNextHeader');
    var i=argv.length>0?parseInt(argv[0]):1;
    while(next_page_el) {
      if (i === 10000) {
        break
      }

      try{
        next_page_el = await page.waitForSelector('#MainContent_lbtnNextHeader',{timeout: 60000});
      }catch(e){
        while(true){
          try{
            await page.goto(ENTRY_URL),{timeout: 60000};
            break
          }catch(e){}
        }
        if((await page.content()).includes('This question is for testing whether you are a human visitor and to prevent automated spam submission.')){
          console.log('Found captcha: resolving')
          resolve_captcha(page) 
        }
        next_page_el = await page.waitForSelector('#MainContent_lbtnNextHeader',{timeout: 60000});
      }
      
      const element = await page.waitForSelector('[name="ctl00$MainContent$txtHeaderCurrentPage"]');
      element.focus()
      const current_page = parseInt(await page.evaluate(x => x.value, element));
      console.log(`current page: ${current_page}, next page: ${i}`);
      const value = `${i}`
      await page.evaluate((x,value) => x.value = value, element,value);
      element.focus()
      await page.keyboard.press('Enter')
      try {
        const httpResponseWeWaitFor = await page.waitForResponse((response) => {
          return response.url().includes("Business/FilingSearch.aspx")
        },{timeout: 15000});  
      } catch(e) {
        while(true){
          try{
            await page.goto(page.url());
            break
          }catch(e){}
        }
        if((await page.content()).includes('This question is for testing whether you are a human visitor and to prevent automated spam submission.')){
          console.log('Found captcha: resolving')
          await resolve_captcha(page)
          const next_page_el = await page.waitForSelector('#MainContent_lbtnNextHeader',{timeout: 120000});
        } 
      }
      await delay(5000)
      await page.waitForSelector('#Ol1',{timeout: 120000});
      const items_urls = await page.evaluate(()=>{
            const ol = document.getElementById('Ol1');
            const urls = Array.prototype.map.call(ol.children,(e)=>e.children[0].getAttribute('href'))
            return urls;
      })

      const last_url = page.url();
      for(let item_url of items_urls){
        console.log(`${BASE_URL}${item_url}`)
        while(true){
        try{
          await page.goto(`${BASE_URL}${item_url}`,{timeout: 60000})
          break
        }catch(e){}
        }
        if((await page.content()).includes('This question is for testing whether you are a human visitor and to prevent automated spam submission.')){
          console.log('Found captcha: resolving')
          await resolve_captcha(page)
        }

        try {
          const data = await page.evaluate(()=>{
            const HISTORY_FILE_REGEX = /\d+/g;
            const el_name = document.getElementById('txtFilingName2');
            const el_id = document.getElementById('txtFilingNum');
            const el_status = document.getElementById('txtStatus');
            const el_txtFilingType = document.getElementById('txtFilingType');
            const el_txtSubStatus = document.getElementById('txtSubStatus');
            const el_txtInitialDate = document.getElementById('txtInitialDate');
            const el_txtStanding = document.getElementById('txtStanding');
            const el_txtStandingRA = document.getElementById('txtStandingRA');
            const el_txtStandingOther = document.getElementById('txtStandingOther');
            const el_txtInactiveDate = document.getElementById('txtInactiveDate');
            const el_txtFormation = document.getElementById('txtFormation');
            const el_txtOfficeAddresss = document.getElementById('txtOfficeAddresss');
            const el_txtMailAddress = document.getElementById('txtMailAddress');
            
            const el_txtAgentName = document.getElementById('txtAgentName');
            const el_txtAgentAddress = document.getElementById('txtAgentAddress');

            const el_txtLatestAR = document.getElementById('txtLatestAR');
            const el_txtARExempt = document.getElementById('txtARExempt');
            const el_txtTaxPaid = document.getElementById('txtTaxPaid');

            const registered_agent = {name: el_txtAgentName?.textContent.trim(), address: el_txtAgentAddress?.textContent.trim()}
            const additional_details = {
              registered_agent,
              latest_ar_year: el_txtLatestAR?.textContent.trim(),
              ar_exempt: el_txtARExempt?.textContent.trim(),
              tax_paid: el_txtTaxPaid?.textContent.trim()
            }


            const divHistorySummary = document.getElementById('divHistorySummary');
            const _hist_sections = divHistorySummary.getElementsByTagName('section');
            const history_data = Array.prototype.map.call(_hist_sections, (hist_section) => {
              const sec1 = hist_section.getElementsByClassName('resHist1')[0];
              const h_title = sec1.innerText.trim();
              const i_file = sec1.children[0];
              const file_data = i_file.getAttribute('onclick')
              const sec2 = hist_section.getElementsByClassName('resHist2')[0];
              const h_date = sec2.innerText.replace('Date:','').trim();
              const sec3 = hist_section.getElementsByClassName('resHist3')[0];
              const h_change = sec3.innerText.trim();


              const FILE_NUMBERS = {}
              const numbersArray = file_data.match(HISTORY_FILE_REGEX);
              if (numbersArray && numbersArray.length >= 2) {
                FILE_NUMBERS['number1'] = numbersArray[0];
                FILE_NUMBERS['number2'] = numbersArray[1];
              } else {
                console.log("Insufficient numbers in the input string.");
                FILE_NUMBERS['number1'] = 0;
                FILE_NUMBERS['number2'] = 0;
              }
              return {h_title, FILE_NUMBERS, h_date, h_change}
            })

            const _divPublicNotes = document.getElementById('divPublicNotes');
            const public_notes = Array.prototype.map.call(_divPublicNotes.children, pbn => {
                return pbn.textContent;
              });

            const _divParties = document.getElementById('divParties')
            const _resHist1 = _divParties.getElementsByClassName('resHist1')
            const _resHist2 = _divParties.getElementsByClassName('resHist2')
            const _resHist3 = _divParties.getElementsByClassName('resHist3')
            const parties = _resHist1&&_resHist2&&_resHist3?{name_type: _resHist1[0]?.textContent, organization: _resHist2[0]?.textContent, address: _resHist3[0]?.textContent}:{}

            return {
              name: el_name?.textContent.trim(),
              id: el_id?.textContent.trim(),
              status: el_status?.textContent.trim(),
              filing_type: el_txtFilingType?.textContent.trim(),
              sub_status: el_txtSubStatus?.textContent.trim(),
              initial_date: el_txtInitialDate?.textContent.trim(),
              standing: el_txtStanding?.textContent.trim(),
              standing_ra: el_txtStandingRA?.textContent.trim(),
              standing_other: el_txtStandingOther?.textContent.trim(),
              inactive_date: el_txtInactiveDate?.textContent.trim(),
              formation: el_txtFormation?.textContent.trim(),
              office_address: el_txtOfficeAddresss?.textContent.trim(),
              mail_address: el_txtMailAddress?.textContent.trim(),
              additional_details,history_data, public_notes, parties
            }
          })
          await fetch('http://127.0.0.1:5000/insert',
                  {
                    method:'POST',
                    body: JSON.stringify(data),
                    headers: {'Content-Type': 'application/json'}
                  }  
              ).then((res)=>res.json())
        } catch(e) {
          console.log(e);
          // await delay(3000000)
        }
      }
      while(true){
        try{
          await page.goto(last_url)
          break
        }catch(e){}
      }
      i +=1
    }
  }
  await page.close()
  await browser.close()
});