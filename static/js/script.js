$(()=>{
    $("#new-pass").on("click", ()=>{
        $("#newpass-modal").css("display", "block");
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
            $(parent).find("img").attr("src", "../static/images/no-eye.png");
            $(input).attr("type", "text");
        }else{
            $(parent).find("img").attr("src", "../static/images/eye.png");
            $(input).attr("type", "password");
        }
    })

    $("#change-master-pass").on("click", (e) =>{        
        AJAXRequest("/changepass", "GET", "", "html", success, error);
        
        function success(data){
            $("#fetched-modal").html(data);
            $("#fetched-modal").css("display", "block");
            $("#fetched-modal").find(".close-btn").click((e)=>{
                $("#fetched-modal").css("display", "none");
            })
        }

        function error(){
            console.log("ERROR");
        }
    })

    $("#delete-master").on("click", (e)=>{
        AJAXRequest("/deleteacc", "GET", "", "html", success, error);

        function success(data){
            $("#fetched-modal").html(data);
            $("#fetched-modal").css("display", "block");
            $("#fetched-modal").find(".close-btn").click((e)=>{
                $("#fetched-modal").css("display", "none");
            })
        }

        function error(){
            console.log("ERROR");
        }
    })
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

