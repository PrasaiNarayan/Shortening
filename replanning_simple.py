

import pandas as pd
from datetime import  timedelta
import math
from Provider import Data_provider
from Provider import Stretch_Flag_setter
import replanning_schedule_manage 
import schedule_manage
import datetime

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
        
        # if row.初回限定=='〇':#done
        #     special_data_of_given_day.at[ind,'firsts']=1
        #     special_data_of_given_day.at[ind,'no_renzoku_seisan']=1

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


# def remaining_planner(unused_class_data,used_class_data):
speciial_records=pd.read_csv("select_data.csv",encoding="utf-8_sig")
speciial_records['納期'] = pd.to_datetime(speciial_records['納期'],format='%Y%m%d')  
speciial_records= func_get_all_variables(speciial_records)
date_list=speciial_records['納期_copy'].tolist()


small_date=datetime.datetime(2022,6,9)
big_date=datetime.datetime(2022,6,10)

# small_date=date_list[0]
# big_date=date_list[0]
# for ele in date_list:
#     if ele<small_date:
#         small_date=ele
    
#     if ele>big_date:
#         big_date=ele

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

# print(speciial_records[['firsts', 'lasts','last_first','品名']])

# speciial_records.to_csv("inter.csv",encoding="utf-8_sig")

Class_Data=[]
class_data1=[]
class_data2=[]


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
# output_file_copy=output_file
# output_file_copy['生産日']=pd.to_datetime(output_file_copy["生産日"],format='%Y-%m-%d')

bigger_Date=pd.to_datetime(big_date)
smaller_Date=pd.to_datetime(small_date)



output_file=output_file[output_file['生産日']>=small_date]
output_file=output_file[output_file['生産日']<=big_date]


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



    class_data2.append(class_data)


Class_Data=class_data1+class_data2


dat=output_file['生産日'].to_list()
dates=[]
for ele in dat:
    if ele not in dates:
        dates.append(ele)


flag_object=[]

# this region creates instances for the dates along with the flags
see_future=3
for ele in dates:
    ibj1= Stretch_Flag_setter(ele,see_future)
    flag_object.append(ibj1)


final_df_range,Class_Data=replanning_schedule_manage.schedule_manager(Class_Data,class_data1,dates,final_df,flag_object,see_future)


abc="replanning"
unused_class_data=schedule_manage.unused_dataframe(Class_Data,non_final_df,abc)

next_planning_class_data=[]
for ele in unused_class_data:
    if ele.get_nouki_copy()>big_date:
        next_planning_class_data.append(ele)


if len(next_planning_class_data)>0:
    class_data3=[]
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



        class_data3.append(class_data)

    new_dat=output_file_copy['生産日'].to_list()

    new_dates=[]
    for ele in new_dat:
        if ele not in new_dates:
            new_dates.append(ele)

    # see_future=3
    new_flag_object=[]
    for ele in new_dates:
        ibj1= Stretch_Flag_setter(ele,see_future)
        new_flag_object.append(ibj1)


    new_class_Data=unused_class_data+class_data3


    last_final_df,Class_Data__=schedule_manage.schedule_manager(new_class_Data,new_dates,last_final_df,new_flag_object,see_future)




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