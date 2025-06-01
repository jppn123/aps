var token = document.cookie.split("=")[1]
var url = "http://127.0.0.1:8000/"
var pgLogin = "login.html"

function removerAcesso(){
    var mydate = new Date();

    window.location = pgLogin;
    mydate.setTime(mydate.getTime() - 1);
    document.cookie = "token=; expires=" + mydate.toGMTString(); 
}

function sair(){
    if(confirm("Realmente deseja sair?")){
        removerAcesso();
    }
}