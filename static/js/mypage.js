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
        console.log(user)
        /*const pwd = rows[0]
        const user_email = rows[0]
        const user_name = rows[0]
        const user_nick = rows[0]*/
        $("#login_id").attr("value",user.id)
        $("#pwd").attr("value",user.pwd)
        $("#user_email").attr("value",user.email)
        $("#user_name").attr("value",user.name)
        $("#user_nick").attr("value",user.nick)

      }
    })
  }

  function modify_page() {
console.log($("#login_id").val())
    $.ajax({
      type: "POST",
      url: '/mypage/modify',
      data: {

        login_id: $("#login_id").val(),
        pwd: $("#pwd").val(),
        nick: $("#user_nick").val()
      },
      success: function(response) {
        console.log(response)
        window.location.reload()
      }

    })
  } 

    function delete_user() {
      id = $("#login_id").val()
      $.ajax({
        type: "DELETE",
        url: '/mypage/delete/'+id,
        data: {
          login_id: $("#login_id").val()
        },
        success: function(response) {
          alert(response.msg)
          window.location.reload()
        }
      })
    }

    // $.ajax({
    //   type: "POST",
    //   url: "/mypage/modify",
    //   data: JSON.stringify ({
    //       login_id: $("#id").val(),
    //       pwd: $("#pwd").val(),
    //       nick: $("#user_nick").val()
          
    //   }),
    //   success: function(response){
    //     show_mypage()
    //     console.log(response)
    //   }
    //   // contentType: "application/json; charset=utf-8"
    
    // })


  
   
  
 

