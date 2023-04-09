$(()=>{
    $("[value='new-pass']").on("click", ()=>{
        $("#newpass-modal").css("display", "block");
    })

    $(".close-btn").on("click", ()=>{
        $("#newpass-modal").css("display", "none");
    })
})


