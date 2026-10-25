/* Земля у моря — лёгкое поведение без сторонних JS-зависимостей */
(function(){
"use strict";
const frame=document.getElementById("ya-form");
const chosen=document.getElementById("chosen-interest");
const params=new URLSearchParams(location.search);
const allowedParams=["utm_source","utm_medium","utm_campaign","utm_content","utm_term","yclid"];
// Сохраняем рекламную атрибуцию у Яндекс Формы, не собирая телефоны в HTML сайта.
if(frame){
 const url=new URL(frame.getAttribute("src"));
 for(const key of allowedParams){
   const val=params.get(key);
   if(val)url.searchParams.set(key,val.slice(0,250));
 }
 frame.src=url.toString();
}
// Клик по карточке сохраняет контекст для человека. Поле внутри iframe
// нельзя корректно заполнить без ID вопроса Яндекс Формы.
document.querySelectorAll("[data-interest]").forEach(function(link){
 link.addEventListener("click",function(){
   const interest=link.getAttribute("data-interest");
   if(chosen&&interest)chosen.textContent="Вы выбрали: "+interest+". Укажите этот вариант в форме.";
 });
});
const menu=document.querySelector(".menu-toggle");
const mobileNav=document.getElementById("mobile-nav");
if(menu&&mobileNav){
 const close=function(){menu.setAttribute("aria-expanded","false");menu.setAttribute("aria-label","Открыть меню");mobileNav.hidden=true;};
 menu.addEventListener("click",function(){
   const opening=menu.getAttribute("aria-expanded")!=="true";
   menu.setAttribute("aria-expanded",String(opening));
   menu.setAttribute("aria-label",opening?"Закрыть меню":"Открыть меню");
   mobileNav.hidden=!opening;
 });
 mobileNav.querySelectorAll("a").forEach(function(a){a.addEventListener("click",close);});
 document.addEventListener("keydown",function(e){if(e.key==="Escape")close();});
}
// Фотографии местности открываются в полном размере. Кадастровые снимки доступны отдельными ссылками.
const viewer=document.getElementById("image-viewer");
const viewerImage=document.getElementById("viewer-img");
const viewerCaption=document.getElementById("viewer-caption");
const viewerClose=viewer&&viewer.querySelector(".viewer-close");
if(viewer&&viewerImage&&viewerClose&&typeof viewer.showModal==="function"){
 document.querySelectorAll(".photo-open").forEach(function(button){
   button.addEventListener("click",function(){
     const img=button.querySelector("img");
     if(!img)return;
     viewerImage.src=img.currentSrc||img.src;
     viewerImage.alt=img.alt;
     viewerCaption.textContent=img.alt;
     viewer.showModal();
   });
 });
 viewerClose.addEventListener("click",function(){viewer.close();});
 viewer.addEventListener("click",function(e){if(e.target===viewer)viewer.close();});
 viewer.addEventListener("close",function(){viewerImage.removeAttribute("src");viewerImage.alt="";});
}
// Панорама проекта «Азгард» загружается только после осознанного клика.
const start=document.getElementById("tour-start");
const panel=document.getElementById("tour-player");
const frameContainer=document.getElementById("tour-frame");
const closeTour=document.getElementById("tour-close");
if(start&&panel&&frameContainer&&closeTour){
 start.addEventListener("click",function(){
   if(frameContainer.querySelector("iframe"))return;
   const iframe=document.createElement("iframe");
   iframe.src="https://azgard-crimea.ru/";
   iframe.title="360-градусный обзор территории проекта «Азгард»";
   iframe.setAttribute("allow","fullscreen; accelerometer; gyroscope");
   iframe.setAttribute("allowfullscreen","");
   iframe.setAttribute("referrerpolicy","no-referrer");
   frameContainer.appendChild(iframe);
   start.hidden=true;panel.hidden=false;start.setAttribute("aria-expanded","true");
   closeTour.focus();
 });
 closeTour.addEventListener("click",function(){
   frameContainer.replaceChildren();
   panel.hidden=true;start.hidden=false;start.setAttribute("aria-expanded","false");
   start.focus();
 });
}
// Мобильная кнопка видна в середине страницы, но не заслоняет шапку и контакты.
const sticky=document.querySelector(".sticky-cta");
const watched=[document.querySelector(".hero"),document.getElementById("zayavka")].filter(Boolean);
if(sticky&&typeof IntersectionObserver==="function"){
 const visible=new Set();
 const observer=new IntersectionObserver(function(entries){
   entries.forEach(function(entry){if(entry.isIntersecting)visible.add(entry.target);else visible.delete(entry.target);});
   sticky.classList.toggle("hide",visible.size>0);
 },{threshold:0.08});
 watched.forEach(function(el){observer.observe(el);});
}
})();