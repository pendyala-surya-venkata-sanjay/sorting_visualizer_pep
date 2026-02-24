import tkinter as tk
from tkinter import ttk
import random

# ---------------- GLOBAL ----------------
data = []
generator = None
running = False
delay = 200
tree = []

# ---------------- CODE ----------------
codes = {
"Bubble Sort":[
"for i in range(n):",
"   for j in range(n-i-1):",
"       if arr[j] > arr[j+1]:",
"           swap"
],
"Merge Sort":[
"divide left",
"divide right",
"merge"
],
"Quick Sort":[
"choose pivot",
"partition",
"sort left",
"sort right"
]
}

def load_code():
    code_box.delete("1.0",tk.END)
    for line in codes.get(algo_var.get(),[]):
        code_box.insert(tk.END,line+"\n")

def highlight(line):
    code_box.tag_remove("hl","1.0",tk.END)
    if line:
        code_box.tag_add("hl",f"{line}.0",f"{line}.end")
        code_box.tag_config("hl",background="yellow")

# ---------------- DRAW ----------------
def draw_array(arr,highlight_idx=[],state="normal"):
    canvas.delete("all")
    w=800
    h=300
    bar=w/len(arr)
    m=max(arr)

    for i,v in enumerate(arr):
        x0=i*bar
        y0=h-(v/m)*280
        x1=(i+1)*bar
        y1=h

        color="cyan"
        if state=="done": color="green"
        elif i in highlight_idx:
            if state=="compare": color="yellow"
            elif state=="swap": color="red"
            elif state=="pivot": color="purple"
            elif state=="divide": color="orange"
            elif state=="merge": color="lightgreen"

        canvas.create_rectangle(x0,y0,x1,y1,fill=color)
        canvas.create_text(x0+bar/2,y0-10,text=str(v),fill="white")

# ---------------- TREE ----------------
def draw_tree():
    tree_canvas.delete("all")
    for i,node in enumerate(tree):
        tree_canvas.create_text(10,20+i*20,anchor="w",text=node,fill="white")

# ---------------- SORT GENERATORS ----------------

def bubble_sort_gen(arr):
    yield arr,[],None,1
    for i in range(len(arr)):
        yield arr,[],None,2
        for j in range(len(arr)-i-1):
            yield arr,[j,j+1],"compare",3
            if arr[j]>arr[j+1]:
                arr[j],arr[j+1]=arr[j+1],arr[j]
                yield arr,[j,j+1],"swap",4
    yield arr,[],"done",None

def merge_sort_gen(arr,l,r,depth=0):
    if l>=r: return
    tree.append("   "*depth+f"merge({l},{r})")
    draw_tree()

    mid=(l+r)//2
    yield arr,list(range(l,mid+1)),"divide",1
    yield from merge_sort_gen(arr,l,mid,depth+1)

    yield arr,list(range(mid+1,r+1)),"divide",2
    yield from merge_sort_gen(arr,mid+1,r,depth+1)

    yield arr,list(range(l,r+1)),"merge",3
    yield from merge(arr,l,mid,r)

def merge(arr,l,m,r):
    left=arr[l:m+1]
    right=arr[m+1:r+1]
    i=j=0
    k=l
    while i<len(left) and j<len(right):
        yield arr,[k],"compare",3
        if left[i]<=right[j]:
            arr[k]=left[i]; i+=1
        else:
            arr[k]=right[j]; j+=1
        yield arr,[k],"swap",3
        k+=1

def quick_sort_gen(arr,low,high,depth=0):
    if low<high:
        tree.append("   "*depth+f"quick({low},{high})")
        draw_tree()

        pi=yield from partition(arr,low,high)
        yield from quick_sort_gen(arr,low,pi-1,depth+1)
        yield from quick_sort_gen(arr,pi+1,high,depth+1)

def partition(arr,low,high):
    pivot=arr[high]
    i=low-1
    for j in range(low,high):
        yield arr,[j,high],"compare",2
        if arr[j]<pivot:
            i+=1
            arr[i],arr[j]=arr[j],arr[i]
            yield arr,[i,j],"swap",2
    arr[i+1],arr[high]=arr[high],arr[i+1]
    yield arr,[i+1],"pivot",1
    return i+1

# ---------------- STEP ----------------
def next_step():
    global generator
    try:
        arr,h,state,line=next(generator)
        draw_array(arr,h,state)
        highlight(line)
    except:
        draw_array(data,[],"done")

# ---------------- AUTO ----------------
def auto():
    if running:
        next_step()
        root.after(delay,auto)

def start_auto():
    global running
    running=True
    auto()

def stop_auto():
    global running
    running=False

# ---------------- CONTROL ----------------
def start_sort():
    global generator,tree
    tree.clear()
    tree_canvas.delete("all")

    arr=data.copy()
    load_code()

    if algo_var.get()=="Bubble Sort":
        generator=bubble_sort_gen(arr)
        tree_frame.pack_forget()
    elif algo_var.get()=="Merge Sort":
        generator=merge_sort_gen(arr,0,len(arr)-1)
        tree_frame.pack(side="right")
    elif algo_var.get()=="Quick Sort":
        generator=quick_sort_gen(arr,0,len(arr)-1)
        tree_frame.pack(side="right")

def generate_array():
    global data
    try:
        data=list(map(int,input_entry.get().split(",")))
    except:
        data=[random.randint(10,100) for _ in range(20)]
    draw_array(data,[])

def change_speed(val):
    global delay
    delay=int(val)

def reset():
    stop_auto()
    draw_array(data,[])

# ---------------- UI ----------------
root=tk.Tk()
root.title("Visualizer Pro")
root.geometry("1200x650")
root.config(bg="#121212")

top=tk.Frame(root,bg="#121212")
top.pack()

input_entry=tk.Entry(top,width=30)
input_entry.grid(row=0,column=0)
input_entry.insert(0,"5,3,8,2,1,7")

algo_var=tk.StringVar()
algo_menu=ttk.Combobox(top,textvariable=algo_var,
values=["Bubble Sort","Merge Sort","Quick Sort"])
algo_menu.current(0)
algo_menu.grid(row=0,column=1)

tk.Button(top,text="Generate",command=generate_array).grid(row=0,column=2)
tk.Button(top,text="Start",command=start_sort).grid(row=0,column=3)
tk.Button(top,text="AUTO",command=start_auto).grid(row=0,column=4)
tk.Button(top,text="STOP",command=stop_auto).grid(row=0,column=5)
tk.Button(top,text="NEXT",command=next_step).grid(row=0,column=6)
tk.Button(top,text="RESET",command=reset).grid(row=0,column=7)

speed=tk.Scale(root,from_=50,to=1000,orient=tk.HORIZONTAL,
label="Speed",command=change_speed)
speed.set(200)
speed.pack()

canvas=tk.Canvas(root,width=800,height=300,bg="black")
canvas.pack(side="left")

tree_frame=tk.Frame(root,bg="#1e1e1e")
tree_canvas=tk.Canvas(tree_frame,width=300,height=300,bg="#1e1e1e")
tree_canvas.pack()

code_box=tk.Text(root,width=40,height=20,bg="#1e1e1e",fg="white")
code_box.pack(side="right")

root.mainloop()