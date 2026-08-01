/* =====================================
   ONLINE QUIZ PLATFORM JAVASCRIPT
===================================== */

// ================================
// Quiz Timer
// ================================


let timeLeft = 60;


let timerElement = document.getElementById("timer");



if(timerElement){


let timer = setInterval(()=>{


timeLeft--;


timerElement.innerHTML =
timeLeft + "s";



if(timeLeft <= 10){

timerElement.style.color="red";

}



if(timeLeft <= 0){


clearInterval(timer);


alert("Time is over! Quiz submitted.");


let quizForm =
document.querySelector("form");


if(quizForm){

quizForm.submit();

}


}



},1000);


}




// ================================
// Progress Bar
// ================================


let questions =
document.querySelectorAll(".question-card");


let progress =
document.querySelector(".progress-bar");



if(questions.length && progress){


let answered=0;



document.querySelectorAll(
"input[type='radio']"
).forEach(option=>{


option.addEventListener(
"change",
()=>{


let name =
option.name;


if(document.querySelector(
"input[name='"+name+"']:checked"
)){

answered++;


let percentage =
(answered/questions.length)*100;



progress.style.width =
percentage+"%";


}


});


});


}




// ================================
// Submit Confirmation
// ================================


let quizForm =
document.querySelector(
"form[action='/submit']"
);



if(quizForm){


quizForm.addEventListener(
"submit",
function(event){


let confirmSubmit =
confirm(
"Are you sure you want to submit quiz?"
);



if(!confirmSubmit){

event.preventDefault();

}


});


}



// ================================
// Disable Double Click Submit
// ================================


document.querySelectorAll(
"button[type='submit']"
)
.forEach(button=>{


button.addEventListener(
"click",
()=>{


button.disabled=true;


button.innerHTML=
"Submitting...";


setTimeout(()=>{


button.disabled=false;


button.innerHTML=
"Submit";


},3000);


});


});
/* =====================================
   ONLINE QUIZ PLATFORM JAVASCRIPT
===================================== */


// ================================
// Password Show / Hide
// ================================


let passwordFields =
document.querySelectorAll(
"input[type='password']"
);


passwordFields.forEach(field=>{


let button =
document.createElement("button");


button.type="button";

button.innerHTML="👁";


button.className=
"btn btn-light";


field.parentNode.appendChild(button);



button.onclick=function(){


if(field.type==="password"){


field.type="text";

button.innerHTML="🙈";


}

else{


field.type="password";

button.innerHTML="👁";


}



};



});





// ================================
// Page Loading Animation
// ================================


window.addEventListener(
"load",
()=>{


document.body.style.opacity="1";


}
);




// ================================
// Smooth Scroll
// ================================


document.querySelectorAll(
"a[href^='#']"
)
.forEach(link=>{


link.addEventListener(
"click",
function(e){


e.preventDefault();



document.querySelector(
this.getAttribute("href")
)
.scrollIntoView({

behavior:"smooth"

});


});


});




// ================================
// Score Percentage Animation
// ================================


let scoreElement =
document.querySelector(".score");



if(scoreElement){


let score =
parseInt(scoreElement.innerText);



let current=0;



let animation =
setInterval(()=>{


if(current>=score){


clearInterval(animation);


}


else{


current++;


scoreElement.innerHTML=
current+"%";


}



},30);



}





// ================================
// Auto Hide Alerts
// ================================
let alerts =
document.querySelectorAll(
".alert"
);



alerts.forEach(alert=>{


setTimeout(()=>{


alert.style.display="none";


},3000);



});




// ================================
// Question Search (Admin)
// ================================


let searchBox =
document.getElementById(
"searchQuestion"
);



if(searchBox){


searchBox.addEventListener(
"keyup",
()=>{


let value =
searchBox.value.toLowerCase();



document.querySelectorAll(
".question-item"
)
.forEach(item=>{


let text =
item.innerText.toLowerCase();



if(text.includes(value)){


item.style.display="block";


}

else{


item.style.display="none";


}



});


});


}




// ================================
// Dark Mode
// ================================


let darkButton =
document.getElementById(
"darkMode"
);



if(darkButton){


darkButton.onclick=function(){


document.body.classList.toggle(
"dark"
);


localStorage.setItem(
"darkMode",
document.body.classList.contains("dark")
);


};


}




// Remember Dark Mode


if(
localStorage.getItem("darkMode")
==="true"
){


document.body.classList.add(
"dark"
);


}





// ================================
// Keyboard Shortcut
// ================================


document.addEventListener(
"keydown",
function(e){



// Press Enter Submit Quiz

if(
e.key==="Enter"
&&
document.querySelector(
"form[action='/submit']"
)

){


document.querySelector(
"form[action='/submit']"
).submit();


}




});




// ================================
// Prevent Refresh During Quiz
// ================================


if(
document.querySelector(
"form[action='/submit']"
)

){


window.onbeforeunload=function(){


return "Quiz is running. Are you sure?";


};


}