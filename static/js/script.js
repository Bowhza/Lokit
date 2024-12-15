$(()=>{
    $("#new-pass").on("click", ()=>{
        $("#newpass-modal").css("display", "flex");
        $("#settings-menu").css("display", "none");
    })

    $(".close-btn").on("click", ()=>{
        $("#newpass-modal").css("display", "none");
    })

    $(".delete-btn").on("click", ()=>{
        let result = confirm("Are you sure you want to delete this entry?");
        if(result === false){
            $(".delete-form").submit((e)=>{
                e.preventDefault();
            })
        }
    })

    $(".show-pass").on("click", (e)=>{
        let parent = e.target.parentElement;
        let input = $(parent).find("input");
        if($(input).attr('type') == "password"){
            $(parent).find(".eye-imgs").attr("src", "../static/images/no-eye.svg");
            $(input).attr("type", "text");
        }else{
            $(parent).find(".eye-imgs").attr("src", "../static/images/eye.svg");
            $(input).attr("type", "password");
        }
    })

    $(".clipboard").on("click", (e)=>{
        let parent = e.target.parentElement;
        let input = parent.children[1];
        console.log(input);
        input.select();
        input.setSelectionRange(0, 99999);
        navigator.clipboard.writeText(input.value);
        alert("Password Copied.");
    })

    $("#settings-btn").on("click", (e)=> {
        $("#settings-menu").css("display", (_, current) => current === "none" ? "grid" : "none");
    })

    $("#change-master-pass").on("click", (e) =>{        
        AJAXRequest("/changepass", "GET", "", "html", success, error);
        
        function success(data){
            $("#fetched-modal").html(data);
            $("#fetched-modal").css("display", "flex");
            $("#fetched-modal").find(".close-btn").click((e)=>{
                $("#fetched-modal").css("display", "none");
            })
            $("#settings-menu").css("display", "none");
        }

        function error(){
            console.log("ERROR");
        }
    })

    $("#delete-master").on("click", (e)=>{
        AJAXRequest("/deleteacc", "GET", "", "html", success, error);

        function success(data){
            $("#fetched-modal").html(data);
            $("#fetched-modal").css("display", "flex");
            $("#fetched-modal").find(".close-btn").click((e)=>{
                $("#fetched-modal").css("display", "none");
            })
            $("#settings-menu").css("display", "none");
        }

        function error(){
            console.log("ERROR");
        }
    })

    $("#generate-password").on("click", ()=>{
        AJAXRequest("/genpass", "GET", "", "html", success, error)

        function success(data){
            $("[name='password1']").val(data);
            $("[name='password2']").val(data);
        }

        function error(data){
            if(data.status == 429){
                alert("Too many requests are being sent. Please wait a minute.")
            }
        }
    })

    const header = document.querySelector("header");
        window.addEventListener("scroll", () => {
            if (window.scrollY > 30) {
                header.classList.add("scrolled");
            } else {
                header.classList.remove("scrolled");
            }
        });
})

function changePassValidation(){
    let newPassword = $("[name='newpassword']").val();
    let confirmPassword = $("[name='confirmpassword']").val();

    if(newPassword != confirmPassword){
        $("[name='newpassword']").css("border-color", "red");
        $("[name='confirmpassword']").css("border-color", "red");
        $("#matching-text").html("The password fields do not match.");
        return false;
    }
}

function formValidation(){
    let password = $("[name='password']").val();
    let confirmPassword = $("[name='confirmpassword']").val();

    if(password != confirmPassword){
        $("[name='password']").css("border-color", "red");
        $("[name='confirmpassword']").css("border-color", "red");
        $("#matching-text").html("The password fields do not match.");
        return false;
    }
}

function AJAXRequest(url, type, data, dataType, success, error){
    options = {
        url: url,
        type: type,
        data: data,
        dataType: dataType,
        success: success,
        error: error
    }

    $.ajax(options);
}