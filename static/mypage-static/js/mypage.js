$(document).ready(function () { 
  show_mypage()
})
  
  function show_mypage() {
    $.ajax({
      type: "GET",
      url: "/mypage/userinfo",
      data: {},
      success: function(response){
        let rows = response["msg"];
        console.log(rows)
        const user = rows[0]
        const pwd = rows[0]
        const user_email = rows[0]
        const user_name = rows[0]
        const user_nick = rows[0]
        $("#login_id").attr("value",user.id)
        $("#pwd").attr("value",user.pwd)
        $("#user_email").attr("value",user.email)
        $("#user_name").attr("value",user.name)
        $("#user_nick").attr("value",user.nick)

      }
    })
  }
 

