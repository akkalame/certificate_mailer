$(function(){
  const links = document.querySelectorAll(".btn-link");

  for (const link of links) {
    link.addEventListener("click", (event) => {
      event.preventDefault();
    });
  }
});

function copy2Clip(texto){
  const elemento = document.createElement("input");
  elemento.setAttribute("type", "text");
  elemento.value = texto;
  document.body.appendChild(elemento);
  elemento.select();
  document.execCommand("copy");
  document.body.removeChild(elemento);
  alertToast({title: "¡Texto Copiado!"});
}