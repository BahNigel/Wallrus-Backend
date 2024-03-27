function getData() {
  var val = document.getElementById('id_design').value;
  document.getElementById('lookup_id_colorway').href = "/admin/designs/colorway/?_to_field=id&q=" + val ;
}
window.onload = function () {
  console.log("ready");

  document.querySelector("[id=lookup_id_colorway]").addEventListener("mousemove", () => {
    getData();
  });

};
