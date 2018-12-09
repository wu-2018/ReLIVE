# ReLIVE - Receptors-Ligands Interaction Visualization Explorer  
  
This is a tool for visualizing interactions between ligands and receptors, initially designed for single-cell RNA-Seq data.  
  
Currently two plot panels are available, the *Cell-Cell plot* and *Cell-Gene Plot*  

![img1](pics/img1.png)  
   
![img2](pics/img2.png)  
  
I'm considering running a website to provide online service for this, but for better performance, please download this repository and run it on your own device.  
  
To do this, simply run:  
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
 
