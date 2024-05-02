const puppeteer = require("puppeteer-extra"); 
const pluginStealth = require("puppeteer-extra-plugin-stealth"); 
 
//save to executable path
const { executablePath } = require("puppeteer"); 
const fs = require('fs');
// Use stealth 
puppeteer.use(pluginStealth());


// file_headers = 'senesteNavn,beliggenhedsadresse,by,coNavn,cvr,email,enhedsnummer,enhedstype,harPseudoCvr,highlightBinavn,highlightHistoriskBinavn,highlightHistoriskHovednavn,hovedbranche,ophoersDato,postnummer,reg,reklameBeskyttet,startDato,status,telefonnummer,virksomhedsform,visNavnPostfix'
// fs.writeFileSync('data.csv', `${file_headers}\n`,  {flag: 'w' })

const args = ['--no-sandbox', '--disable-setuid-sandbox','--start-maximized']

// / Launch puppеteer-stealth 
puppeteer.launch({headless:false, executablePath: executablePath(), args:args , defaultViewPort:null}).then(async browser => { 
	// Create a new page 
    const page = (await browser.pages())[0]
 
	// Set page view 
	// await page.setViewport({ width: 1280, height: 720 }); 
    await page.setRequestInterception(true)
    var headers = null
    var postData = null
    var apiUrl = null
    page.on('request',async(request)=>{    
        if (request.url().includes('/gateway/soeg/fritekst')){
            headers = request.headers()
            postData =  request.postData()
            apiUrl = request.url()
        }
        request.continue()
    })
  

    // page.on('response', async(response) => {
    //     const request = response.request();
    //     if (request.url().includes('/gateway/soeg/fritekst')){
    //         const res = await response.json();
    //         console.log(res);
    //     }
    // })

	// navigate to the website 
	await page.goto("https://datacvr.virk.dk/soegeresultater?enhedstype=virksomhed"); 
	await page.waitForTimeout(10000); 
    
    for(let i=0;i<1000;i++){
        jdata = JSON.parse(postData)
        jdata.fritekstCommand.size = 10
        jdata.fritekstCommand.sideIndex = i
        console.log(jdata)
    
        const params = {
            headers: headers,
            method: "POST",
            body: JSON.stringify(jdata)
        }
    
        const res = await page.evaluate( async(apiUrl,params) => (await fetch(apiUrl,params)).json(),apiUrl,params)
        
        for(let record of res['enheder']){
            row = `${record['senesteNavn']},${record['beliggenhedsadresse'].replaceAll('\n','')},${record['by']},${record['coNavn']},${record['cvr']},${record['email']},${record['enhedsnummer']},${record['enhedstype']},${record['harPseudoCvr']},${record['highlightBinavn']},${record['highlightHistoriskBinavn']},${record['highlightHistoriskHovednavn']},${record['hovedbranche']},${record['ophoersDato']},${record['postnummer']},${record['reg']},${record['reklameBeskyttet']},${record['startDato']},${record['status']},${record['telefonnummer']},${record['virksomhedsform']},${record['visNavnPostfix']}\n`
            fs.writeFileSync('data.csv', row,  {flag: 'a+' })

        }
    
    }


    // console.log(res)
    
	// Wait for page to load
 
	// Take a screenshot 
	// await page.screenshot({ path: "image.png" }); 
 
	// Close the browser 
	// await browser.close(); 
});