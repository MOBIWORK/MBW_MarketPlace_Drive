<template>
    <div>
      <Button @click="startTour">Bắt đầu hướng dẫn</Button>
      <div id="content1">Nội dung 1</div>
      <div id="content2">Nội dung 2</div>
      <Button id="content3" @click="onClickButton()">Call service</Button>
    </div>
  </template>
  
  <script>
  import introJs from "intro.js";
  import "intro.js/introjs.css";
  import {Button} from 'frappe-ui'

  export default {
    components: {
        Button
    },
    methods: {
      startTour() {
        let intro = introJs().setOptions({
            disableInteraction: true,
            showProgress: true,
            showBullets: false,
            nextLabel: "Tiếp",
            prevLabel: "Quay",
            doneLabel: "Xong",
            steps: [
                {
                    title: "Welcome",
                    intro: 'Hello World! 👋'
                },{
                    element: document.getElementById("content1"),
                    intro: 'You cannot select the text because "disableInteraction" is enabled',
                    position: 'right'
                },{
                    element: document.getElementById("content2"),
                    intro: 'This link is not clickable either',
                    position: 'bottom'
                },{
                    title: 'Farewell!',
                    element: document.getElementById("content3"),
                    intro: 'And this is our final step!',
                    position: 'top'
                }
            ]
        });
        intro.start()
        intro.onexit(function(){
            console.log("on exist")
        })
        intro.onbeforechange(function(targetElement){
            console.log("Dòng 52 ", targetElement.id)
        })
        intro.onchange(function(targetElement){
            console.log("Dòng 53 ", targetElement.id)
        })
      },
      onClickButton(){
        console.log("Click Button")
      }
    },
  };
  </script>
  