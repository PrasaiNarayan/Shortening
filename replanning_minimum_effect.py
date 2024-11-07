
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

    for ind,row in speciial_records.iterrows():
        day=row.納期.day_name()
        if day=='Saturday':
            deltas=row.納期-timedelta(days=1)
            speciial_records.at[ind,'納期_copy']=deltas
        elif day=='Sunday':
            deltas=row.納期-timedelta(days=2)
            speciial_records.at[ind,'納期_copy']=deltas


    return speciial_records


#program starts here

see_future=3
speciial_records=pd.read_csv("select_data.csv",encoding="utf-8_sig")
speciial_records['納期'] = pd.to_datetime(speciial_records['納期'],format='%Y%m%d')  
speciial_records= func_get_all_variables(speciial_records)
date_list=speciial_records['納期_copy'].tolist()


output_file1=pd.read_csv("output.csv",encoding="utf-8_sig")
output_file1["生産日"]=pd.to_datetime(output_file1["生産日"],format='%Y-%m-%d')
output_file1["納期"]=pd.to_datetime(output_file1["納期"],format='%Y-%m-%d')


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
                                        row.納期_copy,  #making it noukicopy
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







output_file__=output_file1.copy(deep=True)


output_file_copy1=output_file1.loc[(output_file1['生産日']>big_date)]    #data beyond the range
output_file_copy2=output_file1.loc[(output_file1['生産日']<small_date)]  #data below the small date



# output_file_copy=func_get_all_variables(output_file_copy1)

final_df=pd.DataFrame(columns=output_file1.columns)
last_final_df=pd.DataFrame(columns=output_file1.columns)
non_final_df=pd.DataFrame(columns=output_file1.columns)

output_file_new=func_get_all_variables(output_file__)

remaining_non_planned_data=pd.DataFrame()

unused_class_objects=list()
ticket_no_list=list()
Class_Data=Class_Data+class_data1
counterr=1
while len(class_data1)>0:

    # output_file=output_file_new[(output_file_new['生産日']>=small_date)&(output_file_new['生産日']<=big_date)]
    output_file=output_file_new[output_file_new['生産日']>=small_date]
    output_file=output_file[output_file['生産日']<=big_date]

    output_file["納期_copy"]=pd.to_datetime(output_file["納期_copy"],format='%Y-%m-%d')
    output_file=output_file.sort_values(by='納期_copy')

    

    for data_obj in Class_Data:
        if data_obj.get_ticket_no() not in ticket_no_list:
            ticket_no_list.append(data_obj.get_ticket_no())
   

    current_class_data=[]

    for ind,row in output_file.iterrows():

        if row.チケットNO not in ticket_no_list:

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


    Class_Data=Class_Data+current_class_data

    print(len(Class_Data))



    flag_object2,dates2=falg_object(output_file,see_future)



    final_df_range,Class_Datas,remaining_time=replanning_schedule_manage.schedule_manager(Class_Data,class_data1,dates2,final_df,flag_object2,see_future)

    # print("the remaining time is::::::::::")
    # print(remaining_time)
    # if remaining_time>150:
    #     new_final_df=final_df_range[final_df_range['生産日']<big_date]
    #     output_file_copy2=output_file_copy2.append(new_final_df)
    #     new_output_file=output_file_new[output_file_new['生産日']<=big_date+timedelta(days=3)]
    #     new_output_file=new_output_file[new_output_file['生産日']>big_date]

    #     print(new_output_file)

    #     next_class_data=[]
    #     for ind,row in new_output_file.iterrows():

    #         # if row.チケットNO not in ticket_no_list:

    #         class_data=Data_provider(row.品目コード,
    #                                 row.品名,
    #                                 row.ライン,
    #                                 row.ライン名,
    #                                 row.入目,
    #                                 row.流速,
    #                                 row.テンパリング,
    #                                 row.沃素価,
    #                                 row.KI製品,
    #                                 row.初回限定,
    #                                 row.最終限定,
    #                                 row.リパック,
    #                                 row.予定数量,
    #                                 row.納期,
    #                                 row.チケットNO,
    #                                 row.備考,
    #                                 row.生産日,
    #                                 row.順番,
    #                                 row.slot,
    #                                 row.time_taken,
    #                                 row.納期_copy,
    #                                 row.firsts,
    #                                 row.no_renzoku_seisan,
    #                                 row.clean_time,
    #                                 row.kouyousoka_maya,
    #                                 row.lasts,
    #                                 row.last_first,
    #                                 row.weight_limit,
    #                                 row.only_two,
    #                                 row.mc_renzo,
    #                                 row.stretch_flag,
    #                                 used=0,
    #                                 cleaning_jikan=0)



    #         next_class_data.append(class_data)

    #     for ele in next_class_data:
    #         if  ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:
    #             if ele.get_ticket_no() not in ticket_no_list:
    #                 Class_Data.append(ele)

        # Class_Data=Class_Data+next_class_data


        # dates2=[dates2[-1]]
        # flag_object2=[flag_object2[-1]]
        # class_data2=[]
        # final_df_range,Class_Da,remaining_time=replanning_schedule_manage.schedule_manager(Class_Data,class_data2,dates2,final_df,flag_object2,see_future)







    output_file_copy2=output_file_copy2.append(final_df_range)

    unused_class_objects=[ele for ele in Class_Datas if ele.get_used()==0 and ele.get_nouki_copy()<big_date]
    # unused_class_obj=unused_class_obj+unused_class_objects



    class_data1=[ele for ele in Class_Datas if ele.get_used()==0 and ele.get_nouki_copy()>big_date and ele.get_seisanbi()>=small_date and ele.get_seisanbi()<=big_date]
    unused_class_data=schedule_manage.unused_dataframe(class_data1,non_final_df,str(counterr))
    counterr+=1
    if len(class_data1)>0:
        small_date=big_date+timedelta(days=1)
        big_date=class_data1[0].get_nouki_copy()
        for dates in class_data1:
            if dates.get_nouki_copy()<small_date:
                small_date=dates.get_nouki_copy()

            if dates.get_nouki_copy()>big_date:
                big_date=dates.get_nouki_copy()
        print(small_date,big_date)
        # small_date=pd.to_datetime(small_date)
        # big_date=pd.to_datetime(big_date)

    # else:
    #     remaining_non_planned_data==
output_file_copy1=output_file__.loc[(output_file__['生産日']>big_date)] 

output_file_copy2=output_file_copy2.append(output_file_copy1)


output_file_copy2=output_file_copy2.sort_values(['生産日', '順番'], ascending=[True, True])
output_file_copy2=output_file_copy2.iloc[:, :20]
output_file_copy2.to_csv("output_replanning.csv",encoding="utf-8_sig",index=False)

abc="replanning"
if len(unused_class_objects)>0:
    unused_class_data=schedule_manage.unused_dataframe(unused_class_objects,non_final_df,abc)

