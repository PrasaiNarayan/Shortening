import pandas as pd
import datetime

output=pd.read_csv("output.csv",encoding="utf-8_sig")
output_replanning=pd.read_csv("output_replanning.csv",encoding="utf-8_sig")
output_replanning["compare"]=None

ticket_no=output["チケットNO"].to_list()

ticket_no2=output_replanning["チケットNO"].to_list()

for ele in ticket_no:
    if ele not in ticket_no2:
        print("not available")
        print(ele)
tic=[]
for ele in ticket_no:
    try:
        out_1=output[output["チケットNO"]==ele]["生産日"].values[0]
        out_1=pd.to_datetime(out_1)
        out_3=output_replanning[output_replanning["チケットNO"]==ele]
        out_2=output_replanning[output_replanning["チケットNO"]==ele]["生産日"].values[0]
        out_2=pd.to_datetime(out_2)
        # print(out_1,out_2)

        if out_1==out_2:
            # print(out_3)
            ind=out_3.index
            output_replanning.at[ind,"compare"]=str("〇")


            tic.append(ele)

        else:
            ind=out_3.index
            output_replanning.at[ind,"compare"]=str("×")

    except:
        print("keepup")
        

output_replanning.to_csv("out_replanning.csv",encoding="utf-8_sig",index=False)

print(len(tic))
