
var url = "http://127.0.0.1:8000/"
var pgLogin = "index.html"

function getCookie(nome) {
    var valor = `; ${document.cookie}`;
    var partes = valor.split(`; ${nome}=`);
    if (partes.length === 2) return partes.pop().split(';').shift();
}
    
var token = getCookie("token");
    

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

function VerificarToken(){
    var response;
    fetch(url + "login/validarToken", {
        method: "GET",
        headers: {
            'Authorization': "Bearer " + token                  
        }
    })
    .then(res=>{
        if(res.status != 200){
            removerAcesso();
            return;
        }
        res.json()
        .then(r=>{
            var tipoLogin = r.tp_login
            if(tipoLogin == "adm"){
                document.getElementById("MeusDados").style.display = "none";
                document.getElementById("Sobre").style.display = "none";

                const li = document.createElement("li");
                const a = document.createElement("a");
                const ul = document.querySelector("ul");

                a.id = "login";
                a.href = "inserirLogin.html";
                a.textContent = "Criar Login";

                li.appendChild(a);
                ul.insertBefore(li, ul.lastElementChild);
            } 
            
        })
        
    })
}

function validarDados(){
    if(document.cookie != ""){
        VerificarToken();
    }else{
        alert("Sessão expirada")
        window.location = pgLogin;
        return 
    }
}