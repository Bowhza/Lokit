$(()=>{
    $("[value='new-pass']").on("click", ()=>{
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
})


