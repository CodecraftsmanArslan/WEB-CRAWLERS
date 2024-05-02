const inputString = 'GetImages("030133153078135189066203036160131020015015200043", "143081052037131049174101151060105191121240225143");';
const regex = /\d+/g;
const numbersArray = inputString.match(regex);

if (numbersArray && numbersArray.length >= 2) {
  const number1 = numbersArray[0];
  const number2 = numbersArray[1];
  
  console.log("Number 1:", number1);
  console.log("Number 2:", number2);
} else {
  console.log("Insufficient numbers in the input string.");
}
