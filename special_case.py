
import pandas as pd
from datetime import timedelta
import math
from Provider import Data_provider
import Record_finder
from Provider import Stretch_Flag_setter

def orig_Data_given_day(original_plan,ele):
    original_plan=original_plan[original_plan["生産日"]==ele]
    return original_plan


def special_function(Class_Data_moto,final_df2):
    speciial_records=pd.read_csv("select_data.csv",encoding="utf-8_sig")
    backupclassdata=Class_Data_moto

    speciial_records['納期'] = pd.to_datetime(speciial_records['納期'],format='%Y%m%d')  

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

    date_list=speciial_records['納期_copy'].unique().tolist()
    
    new_Class_data=[]
    for elements in date_list:
        elements=pd.to_datetime(elements)
        
        new_Class_data=[data for data in Class_Data_moto if data.get_seisanbi()!=elements]
        change_to_unused=[data for data in Class_Data_moto if data.get_seisanbi()==elements]
        Class_Data_moto=new_Class_data

        for unable_to_data in change_to_unused:
            unable_to_data.set_used(0)

        # original_plan=orig_Data_given_day(original_plan,elements)
        # special_data_of_given_day=speciial_records[speciial_records['納期']==elements]

        special_data_of_given_day=speciial_records[speciial_records["納期_copy"]==elements]


        Class_Data=[]
        for ind,row in special_data_of_given_day.iterrows():
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
                             used=0,
                             cleaning_jikan=0
                            #  next_renzoku=True

            )
            Class_Data.append(class_data)


        today_data=[]
        for ele in Class_Data:
            today_data.append(ele)
        future_data=change_to_unused
        future_with_today=Class_Data+future_data

        if elements.day_name()=='Sunday' or elements.day_name()=='Saturday':
          
            cleaning_time=30
            total_time=860
        else:

            cleaning_time=20
            total_time=900

        today_first_records=[]
        today_last_records=[]
        
        today_first_records=Record_finder.first_record_finder(today_data,types='○')
        for ele in today_first_records:
            # print(ele.get_KI())
            if ele==today_first_records[0]:
                ele.set_cleaning_time(60)
            else:
                ele.set_cleaning_time(0)
            # print(ele.get_cleaning_time())
        if len(today_first_records)==0:
            today_first_records=Record_finder.first_record_finder_three(today_data,types='MCｼｮｰﾄ')
        
        if len(today_first_records)==0:
            today_first_records=Record_finder.first_record_finder_two(today_data,types='初回限定')

        if len(today_first_records)==0:
            today_first_records=Record_finder.first_record_finder_two(today_data,types='副原料添加なし初回限定')


        total_time_for_today_first_record=0
        for record in today_first_records:      
            total_time_for_today_first_record+=record.get_cleaning_time()+getattr(record,f'get_{line}_time_taken')()+cleaning_time



        today_last_records=Record_finder.last_record_finder(today_data,types='高沃素価')
        rem_jyunko_dekiru=Record_finder.last_record_finder(today_data,types='準高沃素価')

        for ele in rem_jyunko_dekiru:
            today_last_records.append(ele)

        if len(today_last_records)==0:
                today_last_records=Record_finder.last_record_finder(today_data,types='低沃素価')

        if len(today_last_records)==0:
            today_last_records=Record_finder.last_record_finder_two(today_data,types='B')
            rem_arerukon_records=Record_finder.last_record_finder_four_MOS(today_data,types='〇')
            for ele in rem_arerukon_records:
                today_last_records.append(ele)

        if len(today_last_records)==0:
            today_last_records=Record_finder.last_record_finder_three(today_data,types='〇')
        
        
        total_time_for_today_last_records=0
        for record in today_last_records:      
            # before_time=final_time
            # final_time=final_time-timedelta(minutes=record.get_cleaning_time())-timedelta(minutes=getattr(record,f'get_{line}_time_taken')())
            total_time_for_today_last_records+=record.get_cleaning_time()+getattr(record,f'get_{line}_time_taken')()+cleaning_time


        non_priority_record=[]

        total_time_for_non_prior_records=0
        for non_prior in today_data:
            if non_prior.get_used()==0 and non_prior.get_firsts()==0 and non_prior.get_lasts()==0 and non_prior.get_last_first()==0:
                non_priority_record.append(non_prior)
                total_time_for_non_prior_records+=non_prior.get_time_taken()+cleaning_time


        start_time=elements
    
        allowable_start_time=start_time+timedelta(minutes=440)
        # allowable_finish_time=start_time+timedelta(minutes=1380)

        all_records=[]

        if len(today_first_records)>0 and len(today_last_records)>0:
            
            remaining_time=total_time-total_time_for_today_first_record-total_time_for_today_last_records

            non_prior_list=[]
            for ele in non_priority_record:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    non_prior_list.append(ele)
                    remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

            today_with_future_first_records=[]
            if today_first_records[0].get_KI()=='○':
                today_with_future_first_records=Record_finder.first_record_finder(future_with_today,types='○')

                for ele in today_with_future_first_records:
                    if ele==today_with_future_first_records[0]:
                        ele.set_cleaning_time(60)
                    else:
                        ele.set_cleaning_time(0)
                    # print(ele.get_cleaning_time())
                # get_syouhin_name()
            elif today_first_records[0].get_syouhin_name().startswith('MCｼｮｰﾄ'):
                today_with_future_first_records=Record_finder.first_record_finder_three(future_with_today,types='MCｼｮｰﾄ')

            elif today_first_records[0].get_bikou()=='初回限定':
                today_with_future_first_records=Record_finder.first_record_finder_two(future_with_today,types='初回限定')

            elif today_first_records[0].get_bikou()=='副原料添加なし初回限定':
                today_with_future_first_records=Record_finder.first_record_finder_two(future_with_today,types='副原料添加なし初回限定')

            
            for ele in today_with_future_first_records:
                if ele not in today_first_records:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        today_first_records.append(ele)
                        remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                    else:
                        break
            length=len(today_first_records)
            if length>1:
                if today_first_records[0].get_KI()=='○':
                    today_first_records[0].set_cleaning_time(0)
                    today_first_records[-1].set_cleaning_time(60)

            
            today_with_future_last_records=[]
            if today_last_records[0].get_yousoka()=='高沃素価' or today_last_records[0].get_yousoka()=='準高沃素価':
                today_with_future_last_records=Record_finder.last_record_finder(future_with_today,types='高沃素価')
                jyunko_dekiru=Record_finder.last_record_finder(future_with_today,types='準高沃素価')

                for ele in jyunko_dekiru:
                    today_with_future_last_records.append(ele)

            elif today_last_records[0].get_yousoka()=='低沃素価':
                today_with_future_last_records=Record_finder.last_record_finder(future_with_today,types='低沃素価')
            

            elif today_last_records[0].get_Allergy()=='B' or today_last_records[0].get_MOS()=='〇':
                today_with_future_last_records=Record_finder.last_record_finder_two(future_with_today,types='B')
                arerukon_records=Record_finder.last_record_finder_four_MOS(future_with_today,types='〇')
                for ele in arerukon_records:
                    today_with_future_last_records.append(ele)

            elif today_last_records[0].get_saishu_gentei()=='〇':
                today_with_future_last_records=Record_finder.last_record_finder_three(future_with_today,types='〇')

            for ele in today_with_future_last_records:
                if ele not in today_last_records:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        today_last_records.append(ele)
                        remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time


            future_non_prior_list=[]
            for ele in future_data:
                if ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0 and ele.get_used()==0:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        future_non_prior_list.append(ele)
                        remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                    else:
                        break

            today_last_records.reverse() 
            all_records=today_first_records+non_prior_list+future_non_prior_list+today_last_records


        # first finding out whether last end records and first records are present or not
        # if they are empy then go for future records to find the probable first end and last end records
        
        elif len(today_first_records)==0 and len(today_last_records)==0:
            print('both zero')

            future_first_records=[]
            dummy=[]
            for ele in future_data:
                if ele.get_firsts()==1:
                    dummy.append(ele)

            top_rec=None
            if len(dummy)>0:
                top_rec=dummy[0]


            if top_rec!=None:
                
                if top_rec.get_KI()=='○':
                    future_first_records=Record_finder.first_record_finder(future_data,types='○')
                    # print(start_time)

                    for ele in future_first_records:
                        if ele==future_first_records[0]:
                            ele.set_cleaning_time(60)
                        else:
                            ele.set_cleaning_time(0)
                        # print(ele.get_cleaning_time())

                # get_syouhin_name()
                elif top_rec.get_syouhin_name().startswith('MCｼｮｰﾄ'):
                    future_first_records=Record_finder.first_record_finder_three(future_data,types='MCｼｮｰﾄ')

                elif top_rec.get_bikou()=='初回限定':
                    future_first_records=Record_finder.first_record_finder_two(future_data,types='初回限定')

                elif top_rec.get_bikou()=='副原料添加なし初回限定':
                    future_first_records=Record_finder.first_record_finder_two(future_data,types='副原料添加なし初回限定')

        

            # print(f'the length of future_records :{future_data}')
            # for ele in future_data:
            #     print(ele.get_yousoka())
            dummy2=[]
            for ele in future_data:
                if ele.get_lasts()==1 or ele.get_last_first()==1:
                    dummy2.append(ele)

            top_rec2=None
            if len(dummy2)>0:
                top_rec2=dummy2[0]
            future_last_records=[]
            if top_rec2!=None:
                if top_rec2.get_yousoka()=='高沃素価' or top_rec2.get_yousoka()=='準高沃素価':
                    future_last_records=Record_finder.last_record_finder(future_data,types='高沃素価')
                    jyunko_dekiru=Record_finder.last_record_finder(future_data,types='準高沃素価')

                    for ele in jyunko_dekiru:
                        future_last_records.append(ele)

                elif top_rec2.get_yousoka()=='低沃素価':
                    future_last_records=Record_finder.last_record_finder(future_data,types='低沃素価')
            

                elif top_rec2.get_Allergy()=='B' or top_rec2.get_MOS()=='〇':
                    future_last_records=Record_finder.last_record_finder_two(future_data,types='B')
                    arerukon_records=Record_finder.last_record_finder_four_MOS(future_data,types='〇')
                    for ele in arerukon_records:
                        future_last_records.append(ele)

                elif top_rec2.get_saishu_gentei()=='〇':
                    future_last_records=Record_finder.last_record_finder_three(future_data,types='〇')

            # print(f'the length of future_last_records :{future_last_records}')


            future_non_prior_records=[]

            for fut_rec in future_data:
                if fut_rec.get_used()==0 and fut_rec.get_firsts()==0 and fut_rec.get_lasts()==0 and fut_rec.get_last_first()==0:
                    future_non_prior_records.append(fut_rec)



            remaining_time=total_time-total_time_for_non_prior_records
            today_usable_future_last_records=[]
            today_usable_future_first_records=[]


            for prior_recs in future_first_records:
                if remaining_time-prior_recs.get_cleaning_time()-prior_recs.get_time_taken()-cleaning_time>0:
                    today_usable_future_first_records.append(prior_recs)
                    remaining_time=remaining_time-prior_recs.get_cleaning_time()-prior_recs.get_time_taken()-cleaning_time
                else:
                    break
            length=len(today_usable_future_first_records)
            if length>1:
                if today_usable_future_first_records[0].get_KI()=='○':
                    # print(length)
                    today_usable_future_first_records[0].set_cleaning_time(0)
                    today_usable_future_first_records[-1].set_cleaning_time(60)

            # if length==1:
            #     if today_usable_future_first_records[0].get_KI()=='○':
            #         print(f"this is: {today_usable_future_first_records[0].get_cleaning_time()}")


            for prior_recs in future_last_records:
                if remaining_time-prior_recs.get_cleaning_time()-prior_recs.get_time_taken()-cleaning_time>0:
                    today_usable_future_last_records.append(prior_recs)
                    remaining_time=remaining_time-prior_recs.get_cleaning_time()-prior_recs.get_time_taken()-cleaning_time


            for non_prior_recs in future_non_prior_records:
                if remaining_time-non_prior_recs.get_cleaning_time()-non_prior_recs.get_time_taken()-cleaning_time>0:
                    non_priority_record.append(non_prior_recs)
                    remaining_time=remaining_time-prior_recs.get_cleaning_time()-prior_recs.get_time_taken()-cleaning_time
                    

            today_usable_future_last_records.reverse()

            # print(f'today_usable future_first_records :{today_usable_future_first_records}')
            all_records=today_usable_future_first_records+non_priority_record+today_usable_future_last_records
            # print(all_records)

            # for ele in all_records:
            #     print(ele.get_KI())


        elif len(today_first_records)==0 and len(today_last_records)!=0:
            remaining_time=total_time-total_time_for_today_last_records

            today_non_prior_list=[]
            for ele in non_priority_record:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    today_non_prior_list.append(ele)
                    remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time



            future_first_records=[]
            dummy=[]
            for ele in future_data:
                if ele.get_firsts()==1:
                    dummy.append(ele)

            top_rec=None
            if len(dummy)>0:
                top_rec=dummy[0]


            if top_rec!=None:
                if top_rec.get_KI()=='○':
                    future_first_records=Record_finder.first_record_finder(future_data,types='○')
                    for ele in future_first_records:
                        if ele==future_first_records[0]:
                            ele.set_cleaning_time(60)
                        else:
                            ele.set_cleaning_time(0)
                        # print(ele.get_cleaning_time())

                # get_syouhin_name()
                elif top_rec.get_syouhin_name().startswith('MCｼｮｰﾄ'):
                    future_first_records=Record_finder.first_record_finder_three(future_data,types='MCｼｮｰﾄ')

                elif top_rec.get_bikou()=='初回限定':
                    future_first_records=Record_finder.first_record_finder_two(future_data,types='初回限定')

                elif top_rec.get_bikou()=='副原料添加なし初回限定':
                    future_first_records=Record_finder.first_record_finder_two(future_data,types='副原料添加なし初回限定')



            future_first_records_list=[]

            for ele in future_first_records:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    future_first_records_list.append(ele)
                    remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                else:
                    break

            length=len(future_first_records_list)
            if length>1:
                if future_first_records_list[0].get_KI()=='○':
                    future_first_records_list[0].set_cleaning_time(0)
                    future_first_records_list[-1].set_cleaning_time(60)





            # future_last_record_lists_along_with_today

            today_with_future_last_records=[]
            if today_last_records[0].get_yousoka()=='高沃素価' or today_last_records[0].get_yousoka()=='準高沃素価':
                today_with_future_last_records=Record_finder.last_record_finder(future_with_today,types='高沃素価')
                jyunko_dekiru=Record_finder.last_record_finder(future_with_today,types='準高沃素価')

                for ele in jyunko_dekiru:
                    today_with_future_last_records.append(ele)

            elif today_last_records[0].get_yousoka()=='低沃素価':
                today_with_future_last_records=Record_finder.last_record_finder(future_with_today,types='低沃素価')
            

            elif today_last_records[0].get_Allergy()=='B' or today_last_records[0].get_MOS()=='〇':
                today_with_future_last_records=Record_finder.last_record_finder_two(future_with_today,types='B')
                arerukon_records=Record_finder.last_record_finder_four_MOS(future_with_today,types='〇')
                for ele in arerukon_records:
                    today_with_future_last_records.append(ele)

            elif today_last_records[0].get_saishu_gentei()=='〇':
                today_with_future_last_records=Record_finder.last_record_finder_three(future_with_today,types='〇')

            for ele in today_with_future_last_records:
                if ele not in today_last_records:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        today_last_records.append(ele)
                        remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time



            # getting future non prior lists
            future_non_prior_records=[]

            for fut_rec in future_data:
                if fut_rec.get_used()==0 and fut_rec.get_firsts()==0 and fut_rec.get_lasts()==0 and fut_rec.get_last_first()==0:
                    future_non_prior_records.append(fut_rec)

            future_non_prior_list=[]
            for ele in future_non_prior_records:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    future_non_prior_list.append(ele)
                    remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                
            
            today_last_records.reverse()
            all_records=future_first_records_list+today_non_prior_list+future_non_prior_list+today_last_records


            
                
        elif len(today_first_records)!=0 and len(today_last_records)==0:

            remaining_time=total_time-total_time_for_today_first_record

            today_non_prior_list=[]
            for ele in non_priority_record:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    today_non_prior_list.append(ele)
                    remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time


            today_with_future_first_records=[]
            if today_first_records[0].get_KI()=='○':
                today_with_future_first_records=Record_finder.first_record_finder(future_with_today,types='○')

                for ele in today_with_future_first_records:
                    if ele==today_with_future_first_records[0]:
                        ele.set_cleaning_time(60)
                        
                    else:
                        ele.set_cleaning_time(0)

                   
                # get_syouhin_name()
            elif today_first_records[0].get_syouhin_name().startswith('MCｼｮｰﾄ'):
                today_with_future_first_records=Record_finder.first_record_finder_three(future_with_today,types='MCｼｮｰﾄ')

            elif today_first_records[0].get_bikou()=='初回限定':
                today_with_future_first_records=Record_finder.first_record_finder_two(future_with_today,types='初回限定')

            elif today_first_records[0].get_bikou()=='副原料添加なし初回限定':
                today_with_future_first_records=Record_finder.first_record_finder_two(future_with_today,types='副原料添加なし初回限定')

            
            for ele in today_with_future_first_records:
                if ele not in today_first_records:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        today_first_records.append(ele)
                        remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                    else:
                        break

            length=len(today_with_future_first_records)
            if length>1:
                if today_with_future_first_records[0].get_KI()=='○':
                    today_with_future_first_records[0].set_cleaning_time(0)
                    today_with_future_first_records[-1].set_cleaning_time(60)


            dummy2=[]
            for ele in future_data:
                if ele.get_lasts()==1 or ele.get_last_first()==1:
                    dummy2.append(ele)

            top_rec2=None
            if len(dummy2)>0:
                top_rec2=dummy2[0]
            future_last_records=[]
            if top_rec2!=None:
                if top_rec2.get_yousoka()=='高沃素価' or top_rec2.get_yousoka()=='準高沃素価':
                    future_last_records=Record_finder.last_record_finder(future_data,types='高沃素価')
                    jyunko_dekiru=Record_finder.last_record_finder(future_data,types='準高沃素価')

                    for ele in jyunko_dekiru:
                        future_last_records.append(ele)

                elif top_rec2.get_yousoka()=='低沃素価':
                    future_last_records=Record_finder.last_record_finder(future_data,types='低沃素価')
            

                elif top_rec2.get_Allergy()=='B' or top_rec2.get_MOS()=='〇':
                    future_last_records=Record_finder.last_record_finder_two(future_data,types='B')
                    arerukon_records=Record_finder.last_record_finder_four_MOS(future_data,types='〇')
                    for ele in arerukon_records:
                        future_last_records.append(ele)

                elif top_rec2.get_saishu_gentei()=='〇':
                    future_last_records=Record_finder.last_record_finder_three(future_data,types='〇')

            
            future_last_records_list=[]

            for ele in future_last_records:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    future_last_records_list.append(ele)
                    remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time


            # getting future non prior lists
            future_non_prior_records=[]

            for fut_rec in future_data:
                if fut_rec.get_used()==0 and fut_rec.get_firsts()==0 and fut_rec.get_lasts()==0 and fut_rec.get_last_first()==0:
                    future_non_prior_records.append(fut_rec)

            future_non_prior_list=[]
            for ele in future_non_prior_records:
                if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                    future_non_prior_list.append(ele)
                    remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                
            
            future_last_records_list.reverse()
            all_records=today_first_records+today_non_prior_list+future_non_prior_list+future_last_records_list

        task_wise_icrement=0

        # all_records=list(set(all_records))
        i=0
        prev_record=None
        for record in all_records:
            if i==0:
                before_time=allowable_start_time
            else:
                before_time=allowable_start_time+timedelta(minutes=cleaning_time)+timedelta(minutes=prev_record.get_cleaning_time())

            allowable_start_time=before_time+timedelta(minutes=getattr(record,f'get_{line}_time_taken')())
            record.set_slot(before_time,allowable_start_time)
            task_wise_icrement+=1
            record.set_jyounban(task_wise_icrement)

            record.set_seisanbi(start_time)
            record.set_used(1)
            prev_record=record
            i+=1
            
            Class_Data_moto.append(record)


    Class_Data_moto=sorted(new_Class_data, key=lambda x: x.get_seisanbi(), reverse=False)

    # new_date_list=[]
    uniq_date=[]
    for ele in Class_Data_moto:
        date=ele.get_seisanbi()
        # new_date_list.append(date)
        if date not in uniq_date:
            uniq_date.append(date)

  
    whole_data=[]
    for ele in uniq_date:
        particular_data_datewise=[]
        for obj in Class_Data_moto:
            
            if obj.get_seisanbi()==ele:
                particular_data_datewise.append(obj)

        particular_data_datewise=sorted(particular_data_datewise,key=lambda x:x.get_jyounban(),reverse=False)

        for eles in particular_data_datewise:
            whole_data.append(eles)

    for ele in whole_data:  
        final_df2=final_df2.append({'品目コード':ele.get_syouhin_code(),
                            '品名':ele.get_syouhin_name(),
                            'ライン':ele.get_line(),
                            'ライン名':ele.get_line_name(),
                            '入目':ele.get_iri_me(),
                            '流速':ele.get_ryousoku(),
                            'テンパリング':ele.get_tenpahin(),
                            '沃素価':ele.get_yousoka(),
                            'KI':ele.get_KI(),
                            '初回限定':ele.get_syoukai_gentei(),
                            '最終限定':ele.get_saishu_gentei(),
                            'リパック':ele.get_stretch(),
                            '予定数量':ele.get_yotei_syourou(),
                            '納期':ele.get_nouki(),
                            'チケットNO':ele.get_ticket_no(),
                            '備考':ele.get_bikou(),
                            '生産日':ele.get_seisanbi(),
                            '順番':ele.get_jyounban(),
                            'slot':ele.get_slot()

        },
        ignore_index=True)
    
    final_df2.to_csv("output_new.csv",encoding="utf-8_sig",index=False)

    final_df3=pd.DataFrame(columns=final_df2.columns)
    unused_tasks=[ele for ele in backupclassdata if ele.get_used()==0]

    for ele in unused_tasks:
        final_df3=final_df3.append({'品目コード':ele.get_syouhin_code(),
                            '品名':ele.get_syouhin_name(),
                            'ライン':ele.get_line(),
                            'ライン名':ele.get_line_name(),
                            '入目':ele.get_iri_me(),
                            '流速':ele.get_ryousoku(),
                            'テンパリング':ele.get_tenpahin(),
                            '沃素価':ele.get_yousoka(),
                            'KI':ele.get_KI(),
                            '初回限定':ele.get_syoukai_gentei(),
                            '最終限定':ele.get_saishu_gentei(),
                            'リパック':ele.get_stretch(),
                            '予定数量':ele.get_yotei_syourou(),
                            '納期':ele.get_nouki(),
                            'チケットNO':ele.get_ticket_no(),
                            '備考':ele.get_bikou(),
                            '生産日':ele.get_seisanbi(),
                            '順番':ele.get_jyounban(),
                            'slot':ele.get_slot()

        },
        ignore_index=True)
    
    final_df3.to_csv("remaining_new.csv",encoding="utf-8_sig",index=False)

    # return final_df2,Class_Data



df =pd.read_csv("data.csv",encoding="utf-8_sig")
df_moto=df.copy(deep=True)

# special_function(Class_Data,final_df2)


