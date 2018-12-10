# ReLIVE - Receptors-Ligands Interaction Visualization Explorer  
  
This is a tool for visualizing interactions between ligands and receptors, initially designed for single-cell RNA-Seq data.  

Recently I've launched this web app online, available at [https://wu-2018.github.io/relive](https://wu-2018.github.io/relive)  
For better performance, please download this repository and run it on your own device. Follow the instruction at [Deploy](#Deploy)


Currently two plot panels are available, the *Cell-Cell plot* and *Cell-Gene Plot*  

![img1](pics/img1.png)  
   
![img2](pics/img2.png)  
  

## Deploy  
To run it on your own machine, simply run:  
`git clone https://github.com/wu-2018/ReLIVE.git`  
then
`python3 ReLIVE/run.py start`  
Now, your browser will pop up! If not, please manually input and visit `http://localhost:5006`  

## Prerequisite  
* Python3 
* Python3 Libraries:   
    * bokeh>=0.13.0  
    * flask  
    * pandas  
    * scipy  
 
