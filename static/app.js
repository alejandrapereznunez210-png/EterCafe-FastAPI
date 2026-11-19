const API = "/api";
const state = { pedidos: [], productos: [], inventario: [], trabajadores: [], editing: null };
const configs = {
  pedidos: [
    ["cliente","Nombre del cliente","text",true],
    ["producto","Producto solicitado","text",true],
    ["cantidad","Cantidad","number",true],
    ["precio_unitario","Precio unitario (MXN)","number",true],
    ["estado","Estado","select",true,["Pendiente","En preparación","Entregado","Cancelado"]],
    ["observaciones","Observaciones","textarea",false]
  ],
  productos: [
    ["nombre","Nombre del producto","text",true],
    ["categoria","Categoría","select",true,["Cafés","Capuchinos","Lattes","Matcha","Tés","Bebidas sin café","Malteadas"]],
    ["descripcion","Descripción","textarea",false],
    ["precio","Precio (MXN)","number",true],
    ["disponible","Disponibilidad","select",true,["Disponible","No disponible"]]
  ],
  inventario: [
    ["nombre","Nombre del insumo","text",true],
    ["categoria","Categoría","text",true],
    ["cantidad","Cantidad disponible","number",true],
    ["unidad","Unidad (g, ml, piezas...)","text",true],
    ["stock_minimo","Stock mínimo","number",true]
  ],
  trabajadores: [
    ["nombre","Nombre completo","text",true],
    ["puesto","Puesto","text",true],
    ["telefono","Teléfono","tel",false],
    ["correo","Correo electrónico","email",false],
    ["estado","Estado","select",true,["Activo","Inactivo"]]
  ]
};
const labels = {pedidos:"Pedidos",productos:"Menú",inventario:"Inventario",trabajadores:"Trabajadores"};
const money = n => "$" + Number(n || 0).toFixed(2);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const toast = msg => { const t=document.getElementById("toast"); t.textContent=msg; t.classList.add("show"); setTimeout(()=>t.classList.remove("show"),2600); };

async function request(url, options={}) {
  const response = await fetch(url, {headers:{"Content-Type":"application/json"}, ...options});
  const data = response.status === 204 ? null : await response.json();
  if (!response.ok) throw new Error(data?.detail || data?.mensaje || "Ocurrió un error");
  return data;
}
function go(section) {
  document.querySelectorAll(".section-page").forEach(p=>p.classList.remove("active"));
  document.getElementById("page-"+section).classList.add("active");
  document.querySelectorAll(".nav-item").forEach(b=>b.classList.toggle("active",b.dataset.section===section));
  document.getElementById("crumb").textContent=labels[section] || "Inicio";
  document.getElementById("welcome").style.display=section==="inicio"?"flex":"none";
  if(section==="inicio") loadDashboard();
  else loadSection(section);
  window.scrollTo({top:0,behavior:"smooth"});
}
async function loadDashboard(){
  try{
    const d=await request(API+"/dashboard");
    document.getElementById("stat-ventas").textContent=money(d.ventas);
    document.getElementById("stat-pedidos").textContent=d.pedidos;
    document.getElementById("stat-productos").textContent=d.productos;
    document.getElementById("stat-insumos").textContent=d.insumos;
    const orders=await request(API+"/pedidos");
    const host=document.getElementById("recent-orders");
    host.innerHTML=orders.length?orders.slice(0,4).map(o=>`<div class="recent-row"><div class="recent-icon">☕</div><div><b>${esc(o.cliente)}</b><small>${esc(o.producto)} · ${esc(o.estado)}</small></div><div class="recent-total">${money(o.total)}</div></div>`).join(""):`<div class="empty-state">Todavía no hay pedidos. Registra el primero desde el módulo de Pedidos.</div>`;
  }catch(e){toast(e.message)}
}
async function loadSection(section){
  try{
    state[section]=await request(API+"/"+section);
    render(section);
  }catch(e){toast(e.message)}
}
function actionButtons(section,id){return `<div class="actions"><button class="icon-button" title="Editar" onclick="editRecord('${section}',${id})">✎</button><button class="icon-button" title="Eliminar" onclick="removeRecord('${section}',${id})">⌫</button></div>`}
function render(section){
  const data=state[section], count=document.getElementById("count-"+section);
  if(count)count.textContent=`${data.length} registros`;
  if(section==="productos"){
    document.getElementById("product-grid").innerHTML=data.length?data.map(p=>`<article class="product-card"><div class="product-card-top"><div class="product-emoji">${emoji(p.categoria)}</div><span class="category-tag">${esc(p.categoria)}</span></div><h3>${esc(p.nombre)}</h3><p>${esc(p.descripcion||"Producto del menú ÉTER.")}</p><div class="product-card-bottom"><strong class="product-price">${money(p.precio)}</strong><div class="actions"><button class="icon-button" onclick="editRecord('productos',${p.id})">✎</button><button class="icon-button" onclick="removeRecord('productos',${p.id})">⌫</button></div></div><small class="muted">${p.disponible?"Disponible":"No disponible"}</small></article>`).join(""):`<div class="empty-state">Aún no hay productos. Agrega las bebidas de tu menú.</div>`;
    return;
  }
  const host=document.getElementById("table-"+section);
  if(!data.length){host.innerHTML=`<tr><td colspan="8"><div class="empty-state">No hay registros todavía. Utiliza el botón superior para agregar el primero.</div></td></tr>`;return}
  host.innerHTML=data.map(x=>{
    if(section==="pedidos")return `<tr><td class="id-cell">#${x.id}</td><td><b>${esc(x.cliente)}</b></td><td>${esc(x.producto)}</td><td>${x.cantidad}</td><td><b>${money(x.total)}</b></td><td><span class="status">${esc(x.estado)}</span></td><td>${actionButtons(section,x.id)}</td></tr>`;
    if(section==="inventario")return `<tr><td class="id-cell">#${x.id}</td><td><b>${esc(x.nombre)}</b></td><td>${esc(x.categoria)}</td><td>${x.cantidad}</td><td>${esc(x.unidad)}</td><td><span class="status ${Number(x.cantidad)<=Number(x.stock_minimo)?"low":""}">${Number(x.cantidad)<=Number(x.stock_minimo)?"Stock bajo":"En existencia"}</span></td><td>${actionButtons(section,x.id)}</td></tr>`;
    return `<tr><td class="id-cell">#${x.id}</td><td><b>${esc(x.nombre)}</b></td><td>${esc(x.puesto)}</td><td>${esc(x.telefono)}</td><td>${esc(x.correo)}</td><td><span class="status">${esc(x.estado)}</span></td><td>${actionButtons(section,x.id)}</td></tr>`;
  }).join("");
}
function emoji(cat){if(cat==="Matcha")return"🍵";if(cat==="Tés")return"🌼";if(cat==="Malteadas")return"🥤";if(cat==="Bebidas sin café")return"🧋";return"☕"}
function openModal(section, record=null){
  state.editing={section,id:record?.id??null};
  document.getElementById("modal-title").textContent=record?"Editar registro":"Nuevo registro";
  document.getElementById("modal-eyebrow").textContent=labels[section].toUpperCase();
  const host=document.getElementById("form-fields");
  host.innerHTML=configs[section].map(([key,label,type,required,options])=>{
    const val=record?record[key]??"":(key==="estado"?"Pendiente":key==="disponible"?"Disponible":"");
    let input="";
    if(type==="select")input=`<select id="f-${key}" ${required?"required":""}>${options.map(o=>`<option ${String(val)===String(o)?"selected":""}>${o}</option>`).join("")}</select>`;
    else if(type==="textarea")input=`<textarea id="f-${key}" ${required?"required":""}>${esc(val)}</textarea>`;
    else input=`<input id="f-${key}" type="${type}" value="${esc(val)}" ${required?"required":""} ${type==="number"?'min="0" step="any"':""}>`;
    return `<div class="field ${type==="textarea"?"full":""}"><label for="f-${key}">${label}${required?" *":""}</label>${input}</div>`;
  }).join("");
  document.getElementById("modal").classList.add("open");
}
function closeModal(){document.getElementById("modal").classList.remove("open");state.editing=null}
async function editRecord(section,id){try{const r=await request(`${API}/${section}/${id}`);openModal(section,r)}catch(e){toast(e.message)}}
async function removeRecord(section,id){
  if(!confirm("¿Seguro que deseas eliminar este registro? Esta acción no se puede deshacer."))return;
  try{await request(`${API}/${section}/${id}`,{method:"DELETE"});toast("Registro eliminado correctamente");await loadSection(section);if(section==="pedidos")loadDashboard()}catch(e){toast(e.message)}
}
document.getElementById("record-form").addEventListener("submit",async e=>{
  e.preventDefault();if(!state.editing)return;
  const {section,id}=state.editing, payload={};
  configs[section].forEach(([key,,type])=>{
    let val=document.getElementById("f-"+key).value;
    if(type==="number")val=Number(val);
    if(section==="productos"&&key==="disponible")val=val==="Disponible";
    payload[key]=val;
  });
  try{
    await request(id?`${API}/${section}/${id}`:`${API}/${section}`,{method:id?"PUT":"POST",body:JSON.stringify(payload)});
    closeModal();toast(id?"Registro actualizado":"Registro creado correctamente");await loadSection(section);if(section==="pedidos")loadDashboard();
  }catch(err){toast(err.message)}
});
document.querySelectorAll(".nav-item").forEach(b=>b.addEventListener("click",()=>go(b.dataset.section)));
document.querySelectorAll("[data-go]").forEach(b=>b.addEventListener("click",()=>go(b.dataset.go)));
Object.keys(configs).forEach(s=>document.getElementById("add-"+s).addEventListener("click",()=>openModal(s)));
document.getElementById("close-modal").onclick=closeModal;document.getElementById("cancel-modal").onclick=closeModal;
document.getElementById("modal").addEventListener("click",e=>{if(e.target.id==="modal")closeModal()});
document.querySelectorAll("[data-search]").forEach(input=>input.addEventListener("input",()=>{
  const s=input.dataset.search, term=input.value.toLowerCase();
  const filtered=state[s].filter(x=>Object.values(x).join(" ").toLowerCase().includes(term));
  const old=state[s];state[s]=filtered;render(s);state[s]=old;
}));
const date=new Date();document.getElementById("today").textContent=date.toLocaleDateString("es-MX",{weekday:"short",day:"numeric",month:"short",year:"numeric"});
loadDashboard();
