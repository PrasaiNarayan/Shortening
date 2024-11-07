
import pandas as pd
from datetime import  timedelta
import math
from Provider import Data_provider
from Provider import Stretch_Flag_setter
import replanning_schedule_manage 
import schedule_manage
import datetime


def falg_object(output_file,see_future):
    dat=output_file['生産日'].to_list()
    dates=[]
    for ele in dat:
        if ele not in dates:
            dates.append(ele)


    flag_object=[]
    for ele in dates:
        ibj1= Stretch_Flag_setter(ele,see_future)
        flag_object.append(ibj1)

    return flag_object,dates



def func_get_all_variables(speciial_records):
    speciial_records['納期_copy']=speciial_records['納期']
    for ind,row in speciial_records.iterrows():
        day=row.納期.day_name()
        if day=='Saturday':
            deltas=row.納期-timedelta(days=1)
            speciial_records.at[ind,'納期_copy']=deltas
        elif day=='Sunday':
            deltas=row.納期-timedelta(days=2)
            speciial_records.at[ind,'納期_copy']=deltas

    speciial_records['firsts']=0
    speciial_records['lasts']=0
    speciial_records['last_first']=0
    speciial_records['time_taken']=0
    speciial_records['no_renzoku_seisan']=0
    speciial_records['clean_time']=0
    speciial_records['kouyousoka_maya']=0
    speciial_records['arerukon_maya']=0
    speciial_records['weight_limit']=0
    speciial_records['only_two']=0
    speciial_records['mc_renzo']=0
    speciial_records["stretch_flag"]=0

    for ind,row in speciial_records.iterrows():
        time_t=math.ceil(row.予定数量/row.流速*60)
        speciial_records.at[ind,'time_taken']=time_t

        if row.テンパリング=='〇':
            day=row.納期_copy.day_name()
        
            # print(day)
            if day=='Monday':
                deltas=row.納期_copy-timedelta(days=3)
            elif day=='Sunday':
                deltas=row.納期_copy-timedelta(days=2)
            else:
                deltas=row.納期_copy-timedelta(days=1)
            # print(deltas)
            speciial_records.at[ind,'納期_copy']=deltas
            speciial_records.at[ind,'weight_limit']=1  

        if row.リパック=='〇':

            day=row.納期_copy.day_name()
            if day=='Sunday':
                delt=row.納期_copy-timedelta(days=9)
            if day=='Saturday':
                delt=row.納期_copy-timedelta(days=8)
            else:
                delt=row.納期_copy-timedelta(days=7)
            speciial_records.at[ind,'納期_copy']=delt
            speciial_records.at[ind,'stretch_flag']=1

        if row.沃素価=='高沃素価': #done
            speciial_records.at[ind,'lasts']=1
            speciial_records.at[ind,'no_renzoku_seisan']=1

        if row.沃素価=='準高沃素価': #done
            speciial_records.at[ind,'last_first']=1
            speciial_records.at[ind,'kouyousoka_maya']=1

        if row.沃素価=='低沃素価':#done
            speciial_records.at[ind,'last_first']=1

        if row.KI製品=='○':#done
            speciial_records.at[ind,'firsts']=1
            speciial_records.at[ind,'clean_time']=1

        if row.備考=='MO-7S添加品':#done
            speciial_records.at[ind,'lasts']=1
            speciial_records.at[ind,'arerukon_maya']=1

        if row.備考=='副原料添加なし初回限定':#done
            speciial_records.at[ind,'firsts']=1

        if row.備考=='初回限定':#done
            speciial_records.at[ind,'firsts']=1
            speciial_records.at[ind,'no_renzoku_seisan']=1

        if row.品名=='ｲﾄｳIK-NT(H)' or row.品名=='ﾊﾟﾈﾘ-PV(13)':
            speciial_records.at[ind,'mc_renzo']=1


        if row.アレルゲン=='B':#done
            speciial_records.at[ind,'lasts']=1

        if row.品名.startswith('MCｼｮｰﾄ'):#done
            speciial_records.at[ind,'firsts']=1
            speciial_records.at[ind,'only_two']=1

        if row.品名=='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)':#done
            speciial_records.at[ind,'firsts']=1


        if row.最終限定=='〇' :
            speciial_records.at[ind,'lasts']=1


    return speciial_records


#program starts here

see_future=3
speciial_records=pd.read_csv("select_data.csv",encoding="utf-8_sig")
speciial_records['納期'] = pd.to_datetime(speciial_records['納期'],format='%Y%m%d')  
speciial_records= func_get_all_variables(speciial_records)
date_list=speciial_records['納期_copy'].tolist()


small_date=datetime.datetime(2022,6,9)
big_date=datetime.datetime(2022,6,10)


speciial_records=speciial_records.sort_values(['firsts', 'lasts','last_first'], ascending=[False, True,True])

counter=0
for ind,row in speciial_records.iterrows():
    if counter==0:
        speciial_records.at[ind,'納期_copy']=big_date
        prev_counter=counter
    
    else:
        if big_date-timedelta(days=counter)>small_date:
            speciial_records.at[ind,'納期_copy']=big_date-timedelta(days=counter)
            prev_counter=counter
           
        
        else:
            speciial_records.at[ind,'納期_copy']=big_date

    counter=counter+1

Class_Data=[]
class_data1=[]
current_class_data=[]


for ind,row in speciial_records.iterrows():

    class_data=Data_provider(row.品目コード,
                                        row.品名,
                                        row.ライン,
                                        row.ライン名,
                                        row.入目,
                                        row.流速,
                                        row.テンパリング,
                                        row.沃素価,
                                        row.KI製品,
                                        row.初回限定,
                                        row.最終限定,
                                        row.リパック,
                                        row.予定数量,
                                        row.納期,
                                        row.チケットNO,
                                        row.備考,
                                        row.生産日,
                                        row.順番,
                                        row.slot,
                                        row.time_taken,
                                        row.納期_copy,
                                        row.firsts,
                                        row.no_renzoku_seisan,
                                        row.clean_time,
                                        row.kouyousoka_maya,
                                        row.lasts,
                                        row.last_first,
                                        row.weight_limit,
                                        row.only_two,
                                        row.mc_renzo,
                                        row.stretch_flag,
                                        used=0,
                                        cleaning_jikan=0)



    class_data1.append(class_data)



for ele in class_data1:
    ele.set_priority(0)



output_file=pd.read_csv("output.csv",encoding="utf-8_sig")
output_file["生産日"]=pd.to_datetime(output_file["生産日"],format='%Y-%m-%d')
output_file["納期"]=pd.to_datetime(output_file["納期"],format='%Y-%m-%d')



output_file_copy=output_file
output_file_copy1=output_file_copy.loc[(output_file_copy['生産日']>big_date)]
output_file_copy2=output_file_copy.loc[(output_file_copy['生産日']<small_date)]
output_file_copy=func_get_all_variables(output_file_copy1)

final_df=pd.DataFrame(columns=output_file.columns)
last_final_df=pd.DataFrame(columns=output_file.columns)
non_final_df=pd.DataFrame(columns=output_file.columns)
output_file=func_get_all_variables(output_file)

bigger_Date=pd.to_datetime(big_date)
smaller_Date=pd.to_datetime(small_date)

output_file=output_file[output_file['生産日']>=small_date]
output_file=output_file[output_file['生産日']<=big_date]

prev_class_data=[]

for ind,row in output_file_copy2.iterrows():

    class_data=Data_provider(row.品目コード,
                                        row.品名,
                                        row.ライン,
                                        row.ライン名,
                                        row.入目,
                                        row.流速,
                                        row.テンパリング,
                                        row.沃素価,
                                        row.KI製品,
                                        row.初回限定,
                                        row.最終限定,
                                        row.リパック,
                                        row.予定数量,
                                        row.納期,
                                        row.チケットNO,
                                        row.備考,
                                        row.生産日,
                                        row.順番,
                                        row.slot,
                                        row.time_taken,
                                        row.納期_copy,
                                        row.firsts,
                                        row.no_renzoku_seisan,
                                        row.clean_time,
                                        row.kouyousoka_maya,
                                        row.lasts,
                                        row.last_first,
                                        row.weight_limit,
                                        row.only_two,
                                        row.mc_renzo,
                                        row.stretch_flag,
                                        used=0,
                                        cleaning_jikan=0)



    prev_class_data.append(class_data)

flag_object1,dates1=falg_object(output_file_copy2,see_future)

df,class_data10=schedule_manage.schedule_manager(prev_class_data,dates1,final_df,flag_object1,see_future)

# df.to_csv("previous.csv",encoding="utf-8_sig",index=False)

current_class_data=[]

for ind,row in output_file.iterrows():

    class_data=Data_provider(row.品目コード,
                                        row.品名,
                                        row.ライン,
                                        row.ライン名,
                                        row.入目,
                                        row.流速,
                                        row.テンパリング,
                                        row.沃素価,
                                        row.KI製品,
                                        row.初回限定,
                                        row.最終限定,
                                        row.リパック,
                                        row.予定数量,
                                        row.納期,
                                        row.チケットNO,
                                        row.備考,
                                        row.生産日,
                                        row.順番,
                                        row.slot,
                                        row.time_taken,
                                        row.納期_copy,
                                        row.firsts,
                                        row.no_renzoku_seisan,
                                        row.clean_time,
                                        row.kouyousoka_maya,
                                        row.lasts,
                                        row.last_first,
                                        row.weight_limit,
                                        row.only_two,
                                        row.mc_renzo,
                                        row.stretch_flag,
                                        used=0,
                                        cleaning_jikan=0)



    current_class_data.append(class_data)


Class_Data=class_data1+current_class_data+prev_class_data



flag_object2,dates2=falg_object(output_file,see_future)
flag_object2=flag_object2+flag_object1

final_df_range,Class_Datas=replanning_schedule_manage.schedule_manager(Class_Data,class_data1,dates2,final_df,flag_object2,see_future)

abc="replanning"
unused_class_data=schedule_manage.unused_dataframe(Class_Datas,non_final_df,abc)

next_planning_class_data=[]
for ele in unused_class_data:
    if ele.get_nouki_copy()>big_date:
        next_planning_class_data.append(ele)


if len(next_planning_class_data)>0:
    class_data_next=[]
    for ind,row in output_file_copy.iterrows():

        class_data=Data_provider(row.品目コード,
                                            row.品名,
                                            row.ライン,
                                            row.ライン名,
                                            row.入目,
                                            row.流速,
                                            row.テンパリング,
                                            row.沃素価,
                                            row.KI製品,
                                            row.初回限定,
                                            row.最終限定,
                                            row.リパック,
                                            row.予定数量,
                                            row.納期,
                                            row.チケットNO,
                                            row.備考,
                                            row.生産日,
                                            row.順番,
                                            row.slot,
                                            row.time_taken,
                                            row.納期_copy,
                                            row.firsts,
                                            row.no_renzoku_seisan,
                                            row.clean_time,
                                            row.kouyousoka_maya,
                                            row.lasts,
                                            row.last_first,
                                            row.weight_limit,
                                            row.only_two,
                                            row.mc_renzo,
                                            row.stretch_flag,
                                            used=0,
                                            cleaning_jikan=0)



        class_data_next.append(class_data)


    flag_object3,dates3=falg_object(output_file_copy,see_future)
    flag_object3=flag_object3+flag_object2

    class_data_next=Class_Datas+class_data_next
    last_final_df,Class_Data__=schedule_manage.schedule_manager(class_data_next,dates3,last_final_df,flag_object3,see_future)


final_df_range=final_df_range.append(output_file_copy2)
if len(last_final_df)>0:
    final_df_range=final_df_range.append(last_final_df)
else:
     final_df_range=final_df_range.append(output_file_copy1)

final_df_range=final_df_range.sort_values(['生産日', '順番'], ascending=[True, True])
final_df_range.to_csv("output_replanning.csv",encoding="utf-8_sig",index=False)
new_cl_data=Class_Data
for ele in Class_Data__:    
    if ele not in new_cl_data:
        new_cl_data.append(ele)
unused_class_data=schedule_manage.unused_dataframe(new_cl_data,non_final_df,abc)