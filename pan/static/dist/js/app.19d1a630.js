(function(){"use strict";var t={4656:function(t,n,e){var i=e(9242),o=e(3396);function r(t,n,e,i,r,a){const s=(0,o.up)("MainApp");return(0,o.wg)(),(0,o.j4)(s)}var a=e(7139);const s=t=>((0,o.dD)("data-v-f5b3a44a"),t=t(),(0,o.Cn)(),t),c=["id"],u={class:"col"},l={style:{"margin-top":"10px!important","text-align":"right"}},p={class:"col"},f=["onUpdate:modelValue"],v=s((()=>(0,o._)("option",{value:"disabled"},"Desactivado",-1))),d=s((()=>(0,o._)("option",{value:"emitter"},"Origen",-1))),g=s((()=>(0,o._)("option",{value:"receiver"},"Altavoz",-1))),h=[v,d,g],m={class:"col"};function b(t,n,e,r,s,v){return(0,o.wg)(),(0,o.iD)(o.HY,null,[((0,o.wg)(!0),(0,o.iD)(o.HY,null,(0,o.Ko)(s.pains,((t,e)=>((0,o.wg)(),(0,o.iD)("div",{class:"form-inline",key:t.ip},[(0,o._)("div",{class:"row",id:t.ip,style:{"margin-right":"40px"}},[(0,o._)("div",u,[(0,o._)("h3",l,(0,a.zw)(e),1)]),(0,o._)("div",p,[(0,o.wy)((0,o._)("select",{class:"form-control","onUpdate:modelValue":n=>t.status=n},h,8,f),[[i.bM,t.status]])]),(0,o._)("div",m,["receiver"==t.status?((0,o.wg)(),(0,o.iD)("select",{key:0,class:"form-control",onChange:n[0]||(n[0]=(...t)=>v.setIp&&v.setIp(...t))},[((0,o.wg)(!0),(0,o.iD)(o.HY,null,(0,o.Ko)(v.lpains,((t,n)=>((0,o.wg)(),(0,o.iD)("option",{"data-origpai":"pai.ip",key:t.ip,value:"lpai.ip"},(0,a.zw)(n),1)))),128))],32)):(0,o.kq)("",!0)])],8,c)])))),128)),(0,o._)("button",{onClick:n[1]||(n[1]=(...t)=>v.save&&v.save(...t))},"Guardar")],64)}var w=e(6265),_=e.n(w),y={name:"MainApp",props:{},computed:{lpains(){const t=Object.entries(this.pains);return Object.fromEntries(t.filter((t=>"emitter"==t[1].status)))}},mounted(){_().get("/api/config").then((t=>this.pains=t.data))},methods:{save(){for(let t in this.pains)"emitter"==t.status&&(t.remote_ip=t.ip);_().post("api/config",this.pains).then((t=>console.log(t)))},setIp(t){const n=t.target.value,e=t.target.data.origpai;console.log(n),console.log(e)}},data(){return{pains:[]}}},O=e(89);const k=(0,O.Z)(y,[["render",b],["__scopeId","data-v-f5b3a44a"]]);var j=k,x={name:"App",components:{MainApp:j}};const D=(0,O.Z)(x,[["render",r]]);var A=D;const C=(0,i.ri)(A);C.mount("#app"),C.provide("axios",_())}},n={};function e(i){var o=n[i];if(void 0!==o)return o.exports;var r=n[i]={exports:{}};return t[i](r,r.exports,e),r.exports}e.m=t,function(){var t=[];e.O=function(n,i,o,r){if(!i){var a=1/0;for(l=0;l<t.length;l++){i=t[l][0],o=t[l][1],r=t[l][2];for(var s=!0,c=0;c<i.length;c++)(!1&r||a>=r)&&Object.keys(e.O).every((function(t){return e.O[t](i[c])}))?i.splice(c--,1):(s=!1,r<a&&(a=r));if(s){t.splice(l--,1);var u=o();void 0!==u&&(n=u)}}return n}r=r||0;for(var l=t.length;l>0&&t[l-1][2]>r;l--)t[l]=t[l-1];t[l]=[i,o,r]}}(),function(){e.n=function(t){var n=t&&t.__esModule?function(){return t["default"]}:function(){return t};return e.d(n,{a:n}),n}}(),function(){e.d=function(t,n){for(var i in n)e.o(n,i)&&!e.o(t,i)&&Object.defineProperty(t,i,{enumerable:!0,get:n[i]})}}(),function(){e.g=function(){if("object"===typeof globalThis)return globalThis;try{return this||new Function("return this")()}catch(t){if("object"===typeof window)return window}}()}(),function(){e.o=function(t,n){return Object.prototype.hasOwnProperty.call(t,n)}}(),function(){var t={143:0};e.O.j=function(n){return 0===t[n]};var n=function(n,i){var o,r,a=i[0],s=i[1],c=i[2],u=0;if(a.some((function(n){return 0!==t[n]}))){for(o in s)e.o(s,o)&&(e.m[o]=s[o]);if(c)var l=c(e)}for(n&&n(i);u<a.length;u++)r=a[u],e.o(t,r)&&t[r]&&t[r][0](),t[r]=0;return e.O(l)},i=self["webpackChunkstatic"]=self["webpackChunkstatic"]||[];i.forEach(n.bind(null,0)),i.push=n.bind(null,i.push.bind(i))}();var i=e.O(void 0,[998],(function(){return e(4656)}));i=e.O(i)})();
//# sourceMappingURL=app.19d1a630.js.map