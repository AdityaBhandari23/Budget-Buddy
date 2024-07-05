const usernameField=document.querySelector("#usernameField");

const feedBackArea=document.querySelector(".invalid_feedback");

const emailField=document.querySelector("#emailField");
const emailFeedBackArea=document.querySelector(".emailFeedBackArea");

const submitBtn=document.querySelector(".submit-btn")

emailField.addEventListener("keyup", (e)=>{
    // console.log("7E2T7T");
    const emailVal=e.target.value;
    
    emailField.classList.remove("is-invalid");
    emailFeedBackArea.style.display="none";

    if (emailVal.length>0){
        fetch("/authentication/validate-email",{
            body:JSON.stringify({email:emailVal}),
            method:"POST",
        }).then(res=>res.json()).then(data=>{
            console.log('data',data);
            if(data.email_error){
                submitBtn.disabled=true;
                emailField.classList.add("is-invalid");
                emailFeedBackArea.style.display="block";
                emailFeedBackArea.innerHTML=`<p>${data.email_error}</p>`
            }else{
                submitBtn.removeAttribute("disabled");
            }
        });
    }
});


usernameField.addEventListener("keyup",(e)=>{
    // console.log('8888',8888)
    const usernameVal=e.target.value;

    usernameField.classList.remove("is-invalid");
    feedBackArea.style.display="none";

    if (usernameVal.length>0){
        fetch("/authentication/validate-username",{
            body:JSON.stringify({username:usernameVal}),
            method:"POST",
        }).then(res=>res.json()).then(data=>{
            console.log('data',data);
            if(data.username_error){
                submitBtn.disabled=true;
                usernameField.classList.add("is-invalid");
                feedBackArea.style.display="block";
                feedBackArea.innerHTML=`<p>${data.username_error}</p>`
            }else{
                submitBtn.removeAttribute("disabled");
            }
        });
    }
});

