
import pandas as pd
from datetime import  timedelta
import math
from Provider import Data_provider,Stretch_Flag_setter,Date_Class
import replanning_schedule_manage 
import schedule_manage
import datetime
import jaconv


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

# Function to correct values
def correct_string(value):
    if isinstance(value, str):
        # Convert full-width to half-width, except for Katakana
        value = jaconv.z2h(value, kana=False)
        # Replace specific patterns like ｼﾖ- with ｼｮｰ
        value = value.replace('ｼﾖ-', 'ｼｮｰ')
    return value



def func_get_all_variables_type_two(speciial_records):
    speciial_records['納期_copy']=speciial_records['nouki_copy']
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
    speciial_records['SV_time_taken']=0
    speciial_records['SP_time_taken']=0

    speciial_records = speciial_records.applymap(correct_string)

    for ind,row in speciial_records.iterrows():
        # time_t=math.ceil(row['予定数量(㎏)']/row.流速*60)
        # speciial_records.at[ind,'time_taken']=time_t
        if row.SVライン=='〇' and row['SV流量(㎏/h)']!='-' and row.荷姿=='C/S':
            time_SV= math.ceil(row['予定数量(㎏)'] / int(row['SV流量(㎏/h)'].replace(',', ''))*60)
            speciial_records.at[ind,'SV_time_taken']=time_SV

        else:
            speciial_records.at[ind,'SV_time_taken']=0

        if row.SPライン=='〇' and row['SP流量(㎏/h)']!='-':
            time_SP= math.ceil(row['予定数量(㎏)'] / int(row['SP流量(㎏/h)'].replace(',', ''))*60)
            speciial_records.at[ind,'SP_time_taken']=time_SP

        else:
            speciial_records.at[ind,'SP_time_taken']=0


        if row.テンパリング=='〇':
            speciial_records.at[ind,'weight_limit']=1  

        if row.リパック=='〇':
            speciial_records.at[ind,'stretch_flag']=1

        if row.沃素価=='高': #done
            speciial_records.at[ind,'lasts']=1
            speciial_records.at[ind,'no_renzoku_seisan']=1

        if row.沃素価=='準高': #done
            speciial_records.at[ind,'last_first']=1
            speciial_records.at[ind,'kouyousoka_maya']=1

        if row.沃素価=='低':#done
            speciial_records.at[ind,'last_first']=1

        if row.KI製品=='○':#done
            speciial_records.at[ind,'firsts']=1
            speciial_records.at[ind,'clean_time']=1

        if row['MO-7S配合']=='○':#doneMO-7S添加品
            speciial_records.at[ind,'lasts']=1
            speciial_records.at[ind,'arerukon_maya']=1

        # if row.備考=='副原料添加なし初回限定':#done
        if isinstance(row.特記事項, str) and row.特記事項.startswith('副原料無添加品'):
            speciial_records.at[ind,'firsts']=1
            speciial_records.at[ind,'特記事項']='副原料無添'

        # if row.備考=='初回限定':#done
        if row.初回限定 == '〇' and (pd.isna(row.特記事項) or not row.特記事項.startswith('副原料無添加品')) and not row.品名.startswith('MCｼｮｰﾄ'):
            speciial_records.at[ind,'特記事項']='初回限定'
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
    speciial_records['SV_time_taken']=0
    speciial_records['SP_time_taken']=0

    speciial_records = speciial_records.applymap(correct_string)

    for ind,row in speciial_records.iterrows():
        # time_t=math.ceil(row['予定数量(㎏)']/row.流速*60)
        # speciial_records.at[ind,'time_taken']=time_t

        if row.SVライン=='〇' and row['SV流量(㎏/h)']!='-' and row.荷姿=='C/S':
            time_SV= math.ceil(row['予定数量(㎏)'] / int(row['SV流量(㎏/h)'].replace(',', '')))
            speciial_records.at[ind,'SV_time_taken']=time_SV

        else:
            speciial_records.at[ind,'SV_time_taken']=0

        if row.SPライン=='〇' and row['SP流量(㎏/h)']!='-':
            time_SP= math.ceil(row['予定数量(㎏)'] / int(row['SP流量(㎏/h)'].replace(',', '')))
            speciial_records.at[ind,'SP_time_taken']=time_SP

        else:
            speciial_records.at[ind,'SP_time_taken']=0

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

        if row.沃素価=='高': #done
            speciial_records.at[ind,'lasts']=1
            speciial_records.at[ind,'no_renzoku_seisan']=1

        if row.沃素価=='準高': #done
            speciial_records.at[ind,'last_first']=1
            speciial_records.at[ind,'kouyousoka_maya']=1

        if row.沃素価=='低':#done
            speciial_records.at[ind,'last_first']=1

        if row.KI製品=='○':#done
            speciial_records.at[ind,'firsts']=1
            speciial_records.at[ind,'clean_time']=1

        if row['MO-7S配合']=='○':#done
            speciial_records.at[ind,'lasts']=1
            speciial_records.at[ind,'arerukon_maya']=1

        # if row.備考=='副原料添加なし初回限定':#done
        #     speciial_records.at[ind,'firsts']=1

        # if row.備考=='初回限定':#done
        #     speciial_records.at[ind,'firsts']=1
        #     speciial_records.at[ind,'no_renzoku_seisan']=1
        # if row.備考=='副原料添加なし初回限定':#done
        if isinstance(row.特記事項, str) and row.特記事項.startswith('副原料無添加品'):
            speciial_records.at[ind,'firsts']=1
            speciial_records.at[ind,'特記事項']='副原料無添'

        # if row.備考=='初回限定':#done
        if row.初回限定 == '〇' and (pd.isna(row.特記事項) or not row.特記事項.startswith('副原料無添加品')) and not row.品名.startswith('MCｼｮｰﾄ'):
            speciial_records.at[ind,'特記事項']='初回限定'
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
        # if row.納期_copy>datetime.datetime(2022,6,12):
        #     if day=='Saturday':
        #         deltas=row.納期-timedelta(days=1)
        #         speciial_records.at[ind,'納期_copy']= deltas
        #     elif day=='Sunday':
        #         deltas=row.納期-timedelta(days=2)
        #         speciial_records.at[ind,'納期_copy']= deltas


    return speciial_records


#program starts here
#inputs to the program
see_future=3
speciial_records=pd.read_csv("select_data.csv",encoding="utf-8_sig")
master = pd.read_csv("master.csv", encoding="utf-8_sig")
line_names=['SV']
#replan start date
small_date=datetime.datetime(2024,3,1)
#replan end date
big_date=datetime.datetime(2024,3,2)


# Convert both '品目コード' columns to string (object) type before merging
speciial_records['品目コード'] = speciial_records['品目コード'].astype(str)
master['品目コード'] = master['品目コード'].astype(str)

# Perform the merge and add suffixes to overlapping columns (for columns in df_input)
#current special records
speciial_records = pd.merge(speciial_records, master, on='品目コード', how='inner', suffixes=('_input', ''))
# Drop the columns from df_input that are duplicated in master
speciial_records = speciial_records.loc[:, ~speciial_records.columns.str.endswith('_input')]
speciial_records['納期'] = pd.to_datetime(speciial_records['納期'],format='%Y%m%d')  
speciial_records= func_get_all_variables(speciial_records)
date_list=speciial_records['納期_copy'].tolist()
# speciial_records.to_csv('speciial_records.csv',encoding='utf-8_sig',index=False)


#previous　output file
output_file1 = pd.read_csv("output_SV.csv",encoding="utf-8_sig")
output_file1['品目コード'] = output_file1['品目コード'].astype(str)
output_file1 =pd.merge(output_file1, master, on='品目コード', how='inner', suffixes=('_input', ''))
output_file1 = output_file1.loc[:, ~output_file1.columns.str.endswith('_input')]
output_file1["生産日"]= pd.to_datetime(output_file1["生産日"],format='%Y-%m-%d')
output_file1["納期"]= pd.to_datetime(output_file1["納期"],format='%Y-%m-%d')

# output_file1.to_csv("previous_output.csv",encoding='utf-8_sig',index=False)

delta=big_date-small_date
difference_days=delta.days+1

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
                                        None,#row.ライン,
                                        None,#row.ライン名,
                                        row.入目,
                                        None,#row.流速,
                                        row.テンパリング,
                                        
                                        row.沃素価,
                                        row.KI製品,
                                        row.初回限定,
                                        row.最終限定,
                                        # row.リパック,
                                        row.リパック,
                                        row['予定数量(㎏)'],
                                        row.納期,
                                        row['チケットＮＯ'],#row.チケットNO,
                                        # row.備考,
                                        row.特記事項,
                                        row['MO-7S配合'],
                                        row.アレルゲン,
                                        small_date,   #row.生産日, #making noukicopy
                                        None,#row.順番,
                                        None,#row.slot,
                                        # row.time_taken,
                                        row.SV_time_taken,
                                        row.SP_time_taken,
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
                                        row.窒素ガス,
                                        row['SP流量(㎏/h)'],
                                        row['SV流量(㎏/h)'],
                                        row.荷姿,
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

output_file_new=func_get_all_variables_type_two(output_file__)

remaining_non_planned_data=pd.DataFrame()

unused_class_objects=list()
ticket_no_list=list()
Class_Data=Class_Data+class_data1
counterr=1
while len(class_data1)>0:

    # output_file=output_file_new[(output_file_new['生産日']>=small_date)&(output_file_new['生産日']<=big_date)]
    output_file=output_file_new[output_file_new['生産日']==small_date]
    # output_file=output_file[output_file['生産日']<=big_date]

    output_file["納期_copy"]=pd.to_datetime(output_file["納期_copy"],format='%Y-%m-%d')
    output_file=output_file.sort_values(by='納期_copy')

    for data_obj in Class_Data:
        if data_obj.get_ticket_no() not in ticket_no_list:
            ticket_no_list.append(data_obj.get_ticket_no())
   
    current_class_data=[]

    for ind,row in output_file.iterrows():

        if row['チケットＮＯ'] not in ticket_no_list:

            class_data=Data_provider(row.品目コード,
                                                row.品名,
                                                None,# row.ライン,
                                                None,# row.ライン名,
                                                row.入目,
                                                None,#row.流速,
                                                row.テンパリング,
                                                row.沃素価,
                                                row.KI製品,
                                                row.初回限定,
                                                row.最終限定,
                                                # row.リパック,
                                                row.リパック,
                                                row['予定数量(㎏)'],
                                                row.納期,
                                                row['チケットＮＯ'],#row.チケットNO,
                                                # row.備考,
                                                row.特記事項,
                                                row['MO-7S配合'],
                                                row.アレルゲン,
                                                row.生産日,
                                                row.順番,
                                                row.slot,
                                                # row.time_taken,
                                                row.SV_time_taken,
                                                row.SP_time_taken,
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
                                                row.窒素ガス,
                                                row['SP流量(㎏/h)'],
                                                row['SV流量(㎏/h)'],
                                                row.荷姿,
                                                used=0,
                                                cleaning_jikan=0)



            current_class_data.append(class_data)


    Class_Data=current_class_data+Class_Data
    Class_Data=sorted(Class_Data,key=lambda x:(x.get_nouki_copy()),reverse=False)

    flag_object2,dates2=falg_object(output_file,see_future)
    new_bool=counterr<=difference_days

    dates_with_features=[]
    #Addition of code for handaling artificial brakes
    for ele in dates2:
        #user defined break
        #this is the brake that user will include and it can be multiple and has different durations
        long_break_start_time=[]#[ele+timedelta(hours=11)+timedelta(minutes=30)]
        break_duration=[]#[60]
        line_break_pattern={}
        line_break_pattern['break_pattern']={}

        for index,each_brake in enumerate(long_break_start_time):
            if 'break_pattern' not in line_break_pattern:
                line_break_pattern['break_pattern']={}
            line_break_pattern['break_pattern'][f'break{index}']={'break':each_brake,f'break_duration':break_duration[index]}

        each_date_feature=Date_Class(ele,line_break_pattern)
        dates_with_features.append(each_date_feature)



    # final_df_range,Class_Datas,remaining_time=replanning_schedule_manage.schedule_manager(Class_Data,class_data1,dates2,final_df,flag_object2,see_future,new_bool)
    final_df_range,Class_Datas,remaining_time=replanning_schedule_manage.schedule_manager(Class_Data,class_data1,dates_with_features,final_df,flag_object2,see_future,new_bool,line_names)
    
    output_file_copy2=output_file_copy2.append(final_df_range)

    unused_class_objects=[ele for ele in Class_Datas if ele.get_used()==0 and ele.get_nouki_copy()<big_date]

    class_data1=[ele for ele in Class_Datas if ele.get_used()==0 and ele.get_nouki_copy()>small_date]
    unused_class_data=schedule_manage.unused_dataframe(class_data1,non_final_df,str(counterr))
    counterr+=1
    if len(class_data1)>0:
        small=[]
        big_date=class_data1[0].get_nouki_copy()
        for dates in class_data1:
            if dates.get_nouki_copy()>big_date:
                big_date=dates.get_nouki_copy()
        for dates in Class_Data:
            if dates.get_nouki_copy()>small_date and dates.get_nouki_copy()<=big_date:
                small.append(dates.get_nouki_copy())
                
        if len(small)>0:
            small.sort()
            small_date=small[0]

output_file_copy1=output_file__.loc[(output_file__['生産日']>small_date)] 

output_file_copy2=output_file_copy2.append(output_file_copy1)


output_file_copy2=output_file_copy2.sort_values(['生産日', '順番'], ascending=[True, True])
output_file_copy2=output_file_copy2.iloc[:, :20]
output_file_copy2.to_csv("output_replanning.csv",encoding="utf-8_sig",index=False)

abc="replanning"
if len(unused_class_objects)>0:
    unused_class_data=schedule_manage.unused_dataframe(unused_class_objects,non_final_df,abc)

