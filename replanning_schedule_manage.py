
import pandas as pd
from datetime import date, timedelta
import Record_finder

global dates

def stretch_allowable_two_args(original_record,copy_records,flag_object,elements,remaining_time,dates,line):
    
    if elements.day_name()=='Sunday' or elements.day_name()=='Saturday':  
        cleaning_time=30
    else:
        cleaning_time=20

    for record in copy_records:  
        if record.get_stretch_flag()==1:
            for flag_setter in flag_object: 
                if flag_setter.get_nouki_copy()==elements:

                    dictcon=getattr(flag_setter,f'get_dict_{line}')()

                    
                    dates_range_list=[el for el in dates if el<=record.get_nouki_copy() and el>flag_setter.get_nouki_copy()] 
                    day_key=len(dates_range_list)   
                    print(f"the date key {day_key}")
                    print(f"the range list :{dates_range_list}")  

                    dictcon[day_key]=dictcon[day_key]+1
                    print(f"final: {dictcon}")
                    acceptable=True
                    total_stretch_numbers=0
                    for i in range(len(dictcon)):
                        if dictcon[i]>i+1:
                            acceptable=False
                        
                        total_stretch_numbers+=dictcon[i]
                    if total_stretch_numbers>len(dictcon):
                        acceptable=False
                    
                    variant=0

                    for loop_counter in range(len(dictcon)):
                        if dictcon[loop_counter]>loop_counter+1:
                            acceptable=False
                            break

                        if dictcon[loop_counter]==loop_counter+1:
                            for inner_loop in range(loop_counter+1,len(dictcon)):

                                if dictcon[inner_loop]>=inner_loop-variant+1:
                                    acceptable=False
                                    break
                            
                            variant+=1
                            if not acceptable:
                                break


                    if not acceptable:
                        original_record.remove(record)
                        record.set_end_time(record.get_nouki_copy())
                        record.set_st_time(None)
                        record.set_used(0)
                        remaining_time=remaining_time+record.get_cleaning_time()+getattr(record,f'get_{line}_time_taken')()+cleaning_time
                    else:
                        getattr(flag_setter,f'set_dict_{line}')(dictcon)
                        record.set_used(1)
                        record.set_line_name(line)
                    print(f"the acceptable is {acceptable}")

    return original_record,remaining_time




def check_allowable(remaining_time,elements,Class_Data,current_ele,line):
    if elements.day_name()=='Sunday' or elements.day_name()=='Saturday':  
        cleaning_time=30
        total_time=860
    else:
        cleaning_time=20
        total_time=900
    
    current_start_time=total_time-remaining_time
    eligible_start_time=elements+timedelta(minutes=440)+timedelta(minutes=current_start_time)
    previous_day_start_time=eligible_start_time-timedelta(hours=24)

    weight=0
    for ele in Class_Data:
        # print(ele.get_syouhin_name())
        if ele.get_used()==1 and ele.get_weight_limit()==1 and ele.get_line_name()==line:

            if ele.get_end_time()>=previous_day_start_time:

                # print(ele.get_end_time(),ele.get_used(),ele.get_syouhin_name(),eligible_start_time)
                weight+=ele.get_yotei_syourou()
                

    weight+=current_ele.get_yotei_syourou()
   
    current_ele_set_end_time=eligible_start_time+timedelta(minutes=current_ele.get_cleaning_time())+timedelta(minutes=getattr(current_ele,f'get_{line}_time_taken')())+timedelta(minutes=cleaning_time)
    # current_ele.set_end_time(current_ele_set_end_time)

    return weight<51000,current_ele_set_end_time


def check_allowable_two_args(remaining_time,elements,Class_Data,current_ele,line):

    if elements.day_name()=='Sunday' or elements.day_name()=='Saturday':  
        cleaning_time=30
        total_time=860
    else:
        cleaning_time=20
        total_time=900

    current_start_time=total_time-remaining_time
    eligible_start_time=elements+timedelta(minutes=440)+timedelta(minutes=current_start_time)
    previous_day_start_time=eligible_start_time-timedelta(hours=24)

    weight=0
    for ele in Class_Data:
        if ele.get_used()==1 and ele.get_weight_limit()==1 and ele.get_line_name()==line:
            
            if ele.get_end_time()>=previous_day_start_time:
                # print(ele.get_end_time(),ele.get_used(),ele.get_syouhin_name(),eligible_start_time)
                weight+=ele.get_yotei_syourou()
                
                
    
    weight+=current_ele.get_yotei_syourou()
    
    current_ele_set_end_time=eligible_start_time+timedelta(minutes=current_ele.get_cleaning_time())+timedelta(minutes=getattr(current_ele,f'get_{line}_time_taken')())+timedelta(minutes=cleaning_time)
    # current_ele.set_end_time(current_ele_set_end_time)

    return weight<51000,eligible_start_time,current_ele_set_end_time


def fuction_to_allocate(remaining_time,future_with_today,non_prior_list,elements,Class_Data,flag_object,dates,future_with_today_special,line):
    if elements.day_name()=='Sunday' or elements.day_name()=='Saturday':  
        cleaning_time=30
        total_time=860
    else:
        cleaning_time=20
        total_time=900

    non_prior_list1=[]


    time_used_by_tempahin=0
    refrence_remaining_time=remaining_time
    while remaining_time>0:
        
        
        for ele in future_with_today:
           
            non_prior_list2=[]
            if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                if ele.get_weight_limit()==1 and ele.get_used()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:
                    bools,eligible_start_time,current_ele_set_end_time=check_allowable_two_args(remaining_time,elements,Class_Data,ele)
                    if bools:
                        
                        print("IT")
                        # print(f"this time bool: {bools}")
                        ele.set_used(1)
                        ele.set_line_name(line)
                        print(ele.get_ticket_no())
                        non_prior_list2.append(ele)
                        ele.set_st_time(eligible_start_time)
                        ele.set_end_time(current_ele_set_end_time)
                        remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                        # if ele.
                        non_prior_list2,remaining_time=stretch_allowable_two_args(non_prior_list2,non_prior_list2,flag_object,elements,remaining_time,dates)
                        non_prior_list1=non_prior_list1+non_prior_list2
                       
                           
                        
                        if len(non_prior_list2)>0:
                            time_used_by_tempahin=time_used_by_tempahin+ele.get_cleaning_time()+getattr(ele,f'get_{line}_time_taken')()+cleaning_time

   
                    
        remaining_time-=20
    inbetween_time=0
    print("the remain time")
    print(remaining_time)
    if len(non_prior_list1)>0:
        first_element_non_prior_list=non_prior_list1[0].get_st_time()
        startable_time=total_time-refrence_remaining_time
        starting_time_for_now_records=elements+timedelta(minutes=440)+timedelta(minutes=startable_time)

        # print(first_element_non_prior_list)
        # print(starting_time_for_now_records)

        inbetween_time=((first_element_non_prior_list-starting_time_for_now_records).total_seconds())/60

        print(f"inbetween time {inbetween_time}")


    refrence_inbetween_time= inbetween_time
    non_prior_lister=[]
    for ele in future_with_today_special:
        spel=[]
        if ele not in non_prior_list:
             if ele not in non_prior_list1:
                if ele not in non_prior_lister:
                    if ele.get_used()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0 and ele.get_weight_limit()==0:
                        if inbetween_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:

                            ele.set_used(1)
                            ele.set_line_name(line)
                            spel.append(ele)
                            inbetween_time=inbetween_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                            spel,inbetween_time=stretch_allowable_two_args(spel,spel,flag_object,elements,inbetween_time,dates)
                            if len(spel)>0:
                                non_prior_lister.append(ele)
                            # print(inbetween_time)

        


    final_remaining_time=refrence_remaining_time-refrence_inbetween_time-time_used_by_tempahin
    final_non_prior_list=[]

    for ele in future_with_today_special:
        spelll=[]
        if ele not in final_non_prior_list:
            if ele not in non_prior_lister:
                if ele.get_used()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0 and ele.get_weight_limit()==0:
                    if final_remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:  
                        ele.set_used(1)
                        ele.set_line_name(line)
                        spelll.append(ele)
                        final_remaining_time=final_remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                        spelll,final_remaining_time=stretch_allowable_two_args(spelll,spelll,flag_object,elements,final_remaining_time,dates)
                        if len(spelll)>0:
                            final_non_prior_list.append(ele)

                          
    return non_prior_list+non_prior_lister+non_prior_list1+final_non_prior_list



    
def schedule_manager(Class_Data,class_data1,dates_with_features,final_df,flag_object,see_future,new_bool,line_names):
    final_df["nouki_copy"]=None
    #'ライン名',
    
    # final_df_SV=pd.DataFrame(columns=['品目コード','品名','ライン','入目','流速','テンパリング','沃素価','KI製品','初回限定','最終限定','リパック',
    #                                    '予定数量(㎏)','納期','チケットＮＯ','備考','生産日','順番','slot','nouki_copy','窒素ガス','MO-7S配合','アレルゲン',
    #                                    'SP_time_taken','SV_time_taken','SP_rate/hr','SV_rate/hr'])
    
    final_df=pd.DataFrame(columns=['品目コード','品名','ライン', '荷姿','入目','流速','テンパリング','沃素価','KI製品','初回限定','最終限定','リパック',
                                       '予定数量(㎏)','納期','チケットＮＯ','備考','生産日','順番','slot','nouki_copy','窒素ガス','MO-7S配合','アレルゲン',
                                       'SP_time_taken','SV_time_taken','SP_rate/hr','SV_rate/hr','start','end','day'])
    
    
    dates=dates=[ele.date for ele in dates_with_features]
    
    prev_Date=None
    remaining_time=0


    for each_elements in dates_with_features: 
        elements=each_elements.date

        # line_names=['SV','SP']

        for line in line_names:

            if elements.day_name()=='Sunday' or elements.day_name()=='Saturday':
                total_time=860
                cleaning_time=30
            else:
                total_time=900
                cleaning_time=20

            looping_range=len(each_elements.line_break_pattern['break_pattern'])
            breaks={}
            line_break_start=[]
            line_break_duration_list=[]
            if looping_range>0:
                breaks=each_elements.line_break_pattern['break_pattern']

                total_break_time=0
            

                for index, values in enumerate(breaks):
                    break_time=breaks[f'break{index}']['break']
                    break_duration=breaks[f'break{index}']['break_duration']
                    total_break_time+=break_duration
                    line_break_start.append(break_time)
                    line_break_duration_list.append(break_duration)

                
                total_time = total_time-total_break_time


            # print(elements) 
            print (elements)  
            # see_future=3

            #making appropriate dictionary for current date
            if prev_Date!=None:
                for ele in flag_object:
                    
                    if ele.get_nouki_copy()==prev_Date:
                        # print(f"the date {ele.get_nouki_copy()},{prev_Date}")
                        prev_dict=getattr(ele,f'get_dict_{line}')()
                # print(prev_dict)
            if prev_Date!=None:
                for ele in flag_object:
                    if ele.get_nouki_copy()==elements:
                        current_dict={}
                        # print(prev_dict)
                        for cout in range(len(prev_dict)-1):
                            current_dict.update({cout:prev_dict[cout+1]})

                        current_dict.update({len(prev_dict)-1:0})

                        # current_dict={0:prev_dict[1],1:prev_dict[2],2:prev_dict[3],3:0}
                        getattr(ele,f'set_dict_{line}')(current_dict)
            

                        if prev_dict[0]==0:
                            for curren_len in range(len(current_dict)):
                                if current_dict[curren_len]>=1:
                                    current_dict[curren_len]=current_dict[curren_len]-1
                                    break
                                    
                                # elif current_dict[1]>=1:
                                #     current_dict[1]=current_dict[1]-1
                                # elif current_dict[2]>=1:
                                #     current_dict[2]=current_dict[2]-1

                        getattr(ele,f'set_dict_{line}')(current_dict)

                    

        
            today_data=[]
            future_data=[]
            future_with_today=[]
            future_data1=[]
            future_with_today1=[]
            future_with_today_special=[]
            start_time=pd.to_datetime(elements)

            
            for rows_data in Class_Data:
                if rows_data.get_nouki_copy()==start_time and rows_data.get_used()==0 and getattr(rows_data, f'get_{line}_time_taken')()!=0:
                    today_data.append(rows_data)

                if rows_data.get_nouki_copy()>start_time and rows_data.get_used()==0 and getattr(rows_data, f'get_{line}_time_taken')()!=0:
                    if rows_data.get_nouki_copy()<=(start_time+timedelta(days=see_future)) and rows_data.get_mc_renzo()!=1:
                        future_data.append(rows_data)

                if rows_data.get_nouki_copy()>=start_time and rows_data.get_used()==0 and getattr(rows_data, f'get_{line}_time_taken')()!=0:
                    if rows_data.get_nouki_copy()<=(start_time+timedelta(days=see_future)) and rows_data.get_mc_renzo()!=1:
                        future_with_today.append(rows_data)

                if rows_data.get_nouki_copy()>start_time and rows_data.get_used()==0 and getattr(rows_data, f'get_{line}_time_taken')()!=0:
                    if rows_data.get_nouki_copy()<=(start_time+timedelta(days=see_future)):
                        future_data1.append(rows_data)

                if rows_data.get_nouki_copy()>=start_time and rows_data.get_used()==0 and getattr(rows_data, f'get_{line}_time_taken')()!=0:
                    if rows_data.get_nouki_copy()<=(start_time+timedelta(days=see_future)) :
                        future_with_today1.append(rows_data)

                if rows_data.get_nouki_copy()>(start_time+timedelta(days=see_future)) and rows_data.get_used()==0 and getattr(rows_data, f'get_{line}_time_taken')()!=0:
                    if rows_data.get_nouki_copy()<=(start_time+timedelta(days=see_future+3)) :
                        # type1='ｲﾄｳIK-NT(H)', type2='ﾊﾟﾈﾘ-PV(13)'
                        if rows_data.get_syouhin_name()!='ｲﾄｳIK-NT(H)' and rows_data.get_syouhin_name()!='ﾊﾟﾈﾘ-PV(13)':
                            future_with_today_special.append(rows_data)

                
            
            today_data=sorted(today_data,key=lambda x:(x.get_nouki_copy(), x.get_priority()),reverse=False)
            if new_bool:
                for ele in class_data1:
                    if ele.get_used()==0:
                        if ele not in future_data:
                            if ele not in today_data:
                                future_data.append(ele)
                        if ele not in future_data1:
                            if ele not in today_data:
                                future_data1.append(ele)
                        if ele not in future_with_today_special:
                            if ele not in today_data:
                                future_with_today_special.append(ele)
                    
                    

            # future_data.sort(key=lambda x: ( x.get_priority(),x.get_nouki_copy()))

            future_data=sorted(future_data,key=lambda x:( x.get_priority(),x.get_nouki_copy()),reverse=False)
            future_with_today=sorted(future_with_today,key=lambda x:( x.get_nouki_copy(),x.get_priority()),reverse=False)

            future_data1=sorted(future_data1,key=lambda x:( x.get_priority(),x.get_nouki_copy()),reverse=False)

            future_with_today1=sorted(future_with_today1,key=lambda x:( x.get_nouki_copy(),x.get_priority()),reverse=False)

            future_with_today_special=sorted(future_with_today_special,key=lambda x:( x.get_priority(),x.get_nouki_copy()),reverse=False)



            today_first_records=[]
            today_last_records=[]



            today_first_records=Record_finder.first_record_finder(today_data,types='○')
            for ele in today_first_records:
                if ele==today_first_records[0]:
                    ele.set_cleaning_time(60)
                else:
                    ele.set_cleaning_time(0)
                # print(ele.get_cleaning_time())
            if len(today_first_records)==0:
                today_first_records=Record_finder.first_record_finder_three(today_data,types='MCｼｮｰﾄ')
                if len(today_first_records)>0:
                    mc_record=Record_finder.first_record_finder_renzoku(today_data,type1='ｲﾄｳIK-NT(H)', type2='ﾊﾟﾈﾘ-PV(13)')
                    for ele in mc_record:
                        today_first_records.append(ele)
            
            if len(today_first_records)==0:
                today_first_records=Record_finder.first_record_finder_two(today_data,types='初回限定')

            if len(today_first_records)==0:
                today_first_records=Record_finder.first_record_finder_two(today_data,types='副原料無添')
                rem_renzoku_record=Record_finder.first_record_finder_three(today_data,types='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)')
                for re in rem_renzoku_record:
                    if re not in today_first_records:
                        today_first_records.append(re)

                    
            total_time_for_today_first_record=0
            copy_records=today_first_records

            

            for record in copy_records:  
                total_time_for_today_first_record+=record.get_cleaning_time()+getattr(record,f'get_{line}_time_taken')()+cleaning_time



            today_last_records=Record_finder.last_record_finder(today_data,types='高')
            rem_jyunko_dekiru=Record_finder.last_record_finder(today_data,types='準高')

            for ele in rem_jyunko_dekiru:
                today_last_records.append(ele)

            if len(today_last_records)==0:
                    today_last_records=Record_finder.last_record_finder(today_data,types='低')

            if len(today_last_records)==0:
                today_last_records=Record_finder.last_record_finder_two(today_data,types='B')
                rem_arerukon_records=Record_finder.last_record_finder_four_MOS(today_data,types='〇')

                arerukon_re=rem_arerukon_records
                nep=[]
                # shifting record with name ﾊｲDXﾌｱﾂﾄ(H) to last
                for tokui_rec in arerukon_re:
                    if tokui_rec.get_syouhin_name()=='ﾊｲDXﾌｱﾂﾄ(H)':
                        nep.append(tokui_rec)
                        rem_arerukon_records.remove(tokui_rec)
                for ele in nep:
                    rem_arerukon_records.append(ele)

                for ele in rem_arerukon_records:
                    today_last_records.append(ele)

            if len(today_last_records)==0:
                today_last_records=Record_finder.last_record_finder_three(today_data,types='〇')
            
            
            copy_records=today_last_records
            # today_last_records=stretch_allowable(today_last_records,copy_records,flag_object,elements)

            total_time_for_today_last_records=0
            for record in today_last_records:                
                total_time_for_today_last_records+=record.get_cleaning_time()+getattr(record,f'get_{line}_time_taken')()+cleaning_time

            #the data without first and last priority normal elements of the given day

            non_priority_record=[]

            # total_time_for_non_prior_records=0
            for non_prior in today_data:
                if non_prior.get_used()==0 and non_prior.get_firsts()==0 and non_prior.get_lasts()==0 and non_prior.get_last_first()==0:
                
                    non_priority_record.append(non_prior)

            # so that weight_limit elements are allocated at last where thy have better chance of allocation
            non_priority_record=sorted(non_priority_record,key=lambda x:(x.get_weight_limit()),reverse=False)
            allowable_start_time=start_time+timedelta(minutes=440)

            all_records=[]

            if len(today_first_records)>0 and len(today_last_records)>0:
                print("both non zero")
                MC_short_check=False
                
                remaining_time=total_time-total_time_for_today_first_record-total_time_for_today_last_records

                non_prior_list=[]
                still_not_allocated=[]
                for ele in non_priority_record:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        if ele.get_weight_limit()==1:
                            bools,current_ele_set_end_time=check_allowable(remaining_time,elements,Class_Data,ele,line)

                            if bools:
                                ele.set_end_time(current_ele_set_end_time)
                                ele.set_used(1)
                                ele.set_line_name(line)
                                non_prior_list.append(ele)
                                remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                            else:
                                still_not_allocated.append(ele)

                        else:
                            non_prior_list.append(ele)
                            ele.set_used(1)
                            ele.set_line_name(line)
                            remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                today_with_future_first_records=[]
                if today_first_records[0].get_KI()=='○':
                    today_with_future_first_records=Record_finder.first_record_finder(future_with_today,types='○')

                    for ele in today_with_future_first_records:
                        if ele==today_with_future_first_records[0]:
                            ele.set_cleaning_time(60)
                        else:
                            ele.set_cleaning_time(0)

                elif today_first_records[0].get_syouhin_name().startswith('MCｼｮｰﾄ'):
                    today_with_future_first_records=Record_finder.first_record_finder_three(future_with_today,types='MCｼｮｰﾄ')
                    mc_record=Record_finder.first_record_finder_renzoku(future_with_today1,type1='ｲﾄｳIK-NT(H)', type2='ﾊﾟﾈﾘ-PV(13)')
                    for ele in mc_record:
                        today_with_future_first_records.append(ele)

                    MC_short_check=True

                elif today_first_records[0].get_bikou()=='初回限定':
                    today_with_future_first_records=Record_finder.first_record_finder_two(future_with_today,types='初回限定')

                elif today_first_records[0].get_bikou()=='副原料無添' or today_first_records[0].get_syouhin_name()=='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)':
                    today_with_future_first_records=Record_finder.first_record_finder_two(future_with_today,types='副原料無添')
                    rem_renzoku_record=Record_finder.first_record_finder_three(future_with_today,types='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)')
                    for re in rem_renzoku_record:
                        if re not in today_with_future_first_records:
                            today_with_future_first_records.append(re)

                
                for ele in today_with_future_first_records:
                    if ele not in today_first_records:
                        if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                            today_first_records.append(ele)
                            remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                        else:
                            break
                
                today_first_records,remaining_time=stretch_allowable_two_args(today_first_records,today_first_records,flag_object,elements,remaining_time,dates,line)

                refrence_time=remaining_time-total_time_for_today_last_records
                length=len(today_first_records)
                if length>1:
                    if today_first_records[0].get_KI()=='○':
                        today_first_records[0].set_cleaning_time(0)
                        today_first_records[-1].set_cleaning_time(60)

                
                today_with_future_last_records=[]
                if today_last_records[0].get_yousoka()=='高' or today_last_records[0].get_yousoka()=='準高':
                    today_with_future_last_records=Record_finder.last_record_finder(future_with_today,types='高')
                    jyunko_dekiru=Record_finder.last_record_finder(future_with_today,types='準高')

                    for ele in jyunko_dekiru:
                        today_with_future_last_records.append(ele)

                elif today_last_records[0].get_yousoka()=='低':
                    today_with_future_last_records=Record_finder.last_record_finder(future_with_today,types='低')
                

                elif today_last_records[0].get_Allergy()=='B' or today_last_records[0].get_MOS()=='〇':
                    today_with_future_last_records=Record_finder.last_record_finder_two(future_with_today,types='B')
                    arerukon_records=Record_finder.last_record_finder_four_MOS(future_with_today,types='〇')
                    arerukon_re=arerukon_records
                    nep=[]
                    # shifting record with name ﾊｲDXﾌｱﾂﾄ(H) to last
                    for tokui_rec in arerukon_re:
                        if tokui_rec.get_syouhin_name()=='ﾊｲDXﾌｱﾂﾄ(H)':
                            nep.append(tokui_rec)
                            arerukon_records.remove(tokui_rec)

                    for ele in nep:
                        arerukon_records.append(ele)


                    for ele in arerukon_records:
                        today_with_future_last_records.append(ele)

                elif today_last_records[0].get_saishu_gentei()=='〇':
                    today_with_future_last_records=Record_finder.last_record_finder_three(future_with_today,types='〇')

                for ele in today_with_future_last_records:
                    if ele not in today_last_records:
                        if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                            today_last_records.append(ele)
                            remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time


                today_last_records,remaining_time=stretch_allowable_two_args(today_last_records,today_last_records,flag_object,elements,remaining_time,dates,line)




                future_non_prior_list=[]
                future_non_prior_list1=[]
                future_non_prior_list2=[]

                all_data=still_not_allocated
                for ele in future_with_today:
                    if ele not in all_data:
                        all_data.append(ele)
                
                for ele in future_with_today_special:
                    if ele not in all_data:
                        all_data.append(ele)

                


                for i in range(len(all_data)):
                    

                    for ele in all_data:
                        if ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0 and ele.get_used()==0 and ele.get_weight_limit()==1:
                            if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                                # if ele.get_weight_limit()==1:
                                bools,current_ele_set_end_time=check_allowable(refrence_time,elements,Class_Data,ele,line)
                                
                                if bools:
                                    ele.set_end_time(current_ele_set_end_time)
                                    ele.set_used(1)
                                    ele.set_line_name(line)
                                    future_non_prior_list2.append(ele)
                                    remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                                    refrence_time=refrence_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                    for ele in all_data:
                        if ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0 and ele.get_used()==0 and ele.get_weight_limit()==0:
                            if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                                future_non_prior_list2.append(ele)
                                ele.set_used(1)
                                ele.set_line_name(line)
                                remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                                refrence_time=refrence_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                                break



                # using tempahin data upto 7 days and other upto 3 days
                for ele in future_data:
                    if ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0 and ele.get_used()==0 and ele.get_weight_limit()==1:
                        if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                            # if ele.get_weight_limit()==1:
                            bools,current_ele_set_end_time=check_allowable(refrence_time,elements,Class_Data,ele,line)
                            
                            if bools:
                                ele.set_end_time(current_ele_set_end_time)
                                ele.set_used(1)
                                ele.set_line_name(line)
                                future_non_prior_list.append(ele)
                                remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                                refrence_time=refrence_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                    

                future_non_prior_list=future_non_prior_list2+future_non_prior_list

                future_non_prior_list,remaining_time=stretch_allowable_two_args(future_non_prior_list,future_non_prior_list,flag_object,elements,remaining_time,dates,line)

                for ele in future_data:
                    if ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0 and ele.get_used()==0 and ele.get_weight_limit()==0:
                        if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                            future_non_prior_list1.append(ele)
                            ele.set_used(1)
                            ele.set_line_name(line)
                            remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                future_non_prior_list1,remaining_time=stretch_allowable_two_args(future_non_prior_list1,future_non_prior_list1,flag_object,elements,remaining_time,dates,line)

                future_non_prior_list=future_non_prior_list+future_non_prior_list1
                today_last_records.reverse() 

            # adding record with names 'ｲﾄｳIK-NT(H)' and 'ﾊﾟﾈﾘ-PV(13)' just after the record with name 'MCｼｮｰﾄ' 
                for ele in non_prior_list:
                    ele.set_used(1)
                    ele.set_line_name(line)

                non_prior_list=fuction_to_allocate(remaining_time,future_with_today,non_prior_list,elements,Class_Data,flag_object,dates,future_with_today_special,line)


                today_last_records.reverse()

                non_pror=non_prior_list+future_non_prior_list
                if MC_short_check:
                    OP=[]
                    GP=non_pror
                    for ele in GP:
                        if ele.get_syouhin_name()=='ｲﾄｳIK-NT(H)' or ele.get_syouhin_name()=='ﾊﾟﾈﾘ-PV(13)':
                            non_pror.remove(ele)
                            OP.append(ele)

                    today_first_records=today_first_records+OP


                


                all_records=today_first_records+non_pror+today_last_records


            # first finding out whether last end records and first records are present or not
            # if they are empy then go for future records to find the probable first end and last end records
            
            elif len(today_first_records)==0 and len(today_last_records)==0:
                print('both zero')
                MC_short_check=False
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

                        mc_record=Record_finder.first_record_finder_renzoku(future_data1,type1='ｲﾄｳIK-NT(H)', type2='ﾊﾟﾈﾘ-PV(13)')
                        for ele in mc_record:
                            future_first_records.append(ele)

                        MC_short_check=True

                    elif top_rec.get_bikou()=='初回限定':
                        future_first_records=Record_finder.first_record_finder_two(future_data,types='初回限定')

                    elif top_rec.get_bikou()=='副原料無添' or top_rec.get_syouhin_name()=='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)':
                        future_first_records=Record_finder.first_record_finder_two(future_data,types='副原料無添')
                        rem_renzoku_record=Record_finder.first_record_finder_three(future_data,types='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)')
                        
                        for re in rem_renzoku_record:
                            if re not in future_first_records:
                                future_first_records.append(re)

                dummy2=[]
                for ele in future_data:
                    if ele.get_lasts()==1 or ele.get_last_first()==1:
                        dummy2.append(ele)

                top_rec2=None
                if len(dummy2)>0:
                    top_rec2=dummy2[0]
                future_last_records=[]
                if top_rec2!=None:
                    if top_rec2.get_yousoka()=='高' or top_rec2.get_yousoka()=='準高':
                        future_last_records=Record_finder.last_record_finder(future_data,types='高')
                        jyunko_dekiru=Record_finder.last_record_finder(future_data,types='準高')

                        for ele in jyunko_dekiru:
                            future_last_records.append(ele)

                    elif top_rec2.get_yousoka()=='低':
                        future_last_records=Record_finder.last_record_finder(future_data,types='低')
                

                    elif top_rec2.get_Allergy()=='B' or top_rec2.get_MOS()=='〇':
                
                        future_last_records=Record_finder.last_record_finder_two(future_data,types='B')
                        arerukon_records=Record_finder.last_record_finder_four_MOS(future_data,types='〇')

                        arerukon_re=arerukon_records
                        nep=[]
                        # shifting record with name ﾊｲDXﾌｱﾂﾄ(H) to last
                        for tokui_rec in arerukon_re:
                            if tokui_rec.get_syouhin_name()=='ﾊｲDXﾌｱﾂﾄ(H)':
                                nep.append(tokui_rec)
                                arerukon_records.remove(tokui_rec)
                        for ele in nep:
                            arerukon_records.append(ele)


                        for ele in arerukon_records:
                            future_last_records.append(ele)

                    elif top_rec2.get_saishu_gentei()=='〇':
                        future_last_records=Record_finder.last_record_finder_three(future_data,types='〇')


                remaining_time=total_time#-total_time_for_non_prior_records
                # handeling non priority records
                still_not_allocated=[]
                non_prior_list=[]
                for ele in non_priority_record:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        print("the shyouhin name is :::")
                        print(ele.get_syouhin_name())
                        if ele.get_weight_limit()==1:
                            
                            bools,current_ele_set_end_time=check_allowable(remaining_time,elements,Class_Data,ele,line)
                            print(bools)
                        
                    
                            if bools:
                                ele.set_end_time(current_ele_set_end_time)
                                ele.set_used(1)
                                ele.set_line_name(line)
                                non_prior_list.append(ele)
                                remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                            if not bools:
                                still_not_allocated.append(ele)


                        else:
                            non_prior_list.append(ele)
                            ele.set_used(1)
                            ele.set_line_name(line)
                            remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time


                non_prior_list,remaining_time=stretch_allowable_two_args(non_prior_list,non_prior_list,flag_object,elements,remaining_time,dates,line)

                today_usable_future_last_records=[]
                today_usable_future_first_records=[]


                for ele in future_first_records:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        today_usable_future_first_records.append(ele)
                        remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                    else:
                        break
                length=len(today_usable_future_first_records)
                for ele in future_first_records:
                    print(ele.get_ticket_no())

                if length>1:
                    if today_usable_future_first_records[0].get_KI()=='○':
                        # print(length)
                        today_usable_future_first_records[0].set_cleaning_time(0)
                        today_usable_future_first_records[-1].set_cleaning_time(60)

                today_usable_future_first_records,remaining_time=stretch_allowable_two_args(today_usable_future_first_records,today_usable_future_first_records,flag_object,elements,remaining_time,dates,line)

                refrence_time=remaining_time

                for ele in future_last_records:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        
                        if ele.get_weight_limit()==1:
                            bools,current_ele_set_end_time=check_allowable(remaining_time,elements,Class_Data,ele,line)
                            if bools:
                                ele.set_end_time(current_ele_set_end_time)
                                ele.set_used(1)
                                ele.set_line_name(line)
                                today_usable_future_last_records.append(ele)
                                remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                        else:
                            today_usable_future_last_records.append(ele)
                            remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                today_usable_future_last_records,remaining_time=stretch_allowable_two_args(today_usable_future_last_records,today_usable_future_last_records,flag_object,elements,remaining_time,dates,line)
                
                non_prior_list1=[]
                non_prior_list2=[]
                non_prior_list3=[]


                all_data=still_not_allocated
                for ele in future_with_today:
                    if ele not in all_data:
                        all_data.append(ele)
                
                for ele in future_with_today_special:
                    if ele not in all_data:
                        all_data.append(ele)

            


                for i in range (len(all_data)):

                
                    for ele in all_data:
                        # print("The still rec;;;;;")
                        if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                            if ele.get_weight_limit()==1 and ele.get_used()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:

                                bools,current_ele_set_end_time=check_allowable(refrence_time,elements,Class_Data,ele,line)

                                if bools:
                                    
                                    ele.set_end_time(current_ele_set_end_time)
                                    ele.set_used(1)
                                    ele.set_line_name(line)
                                    non_prior_list3.append(ele)
                                    remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                                    refrence_time=refrence_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                    

                    for ele in all_data:
                        # print(ele.get_syouhin_name())
                        if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0 and ele.get_used()==0:
                            if ele.get_weight_limit()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:
                                ele.set_used(1)
                                ele.set_line_name(line)
                                non_prior_list3.append(ele)
                                remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                                refrence_time=refrence_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                                # print(ele.get_ticket_no())


                                break

                for ele in future_data:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0 and ele.get_used()==0:
                        if ele.get_weight_limit()==1 and ele.get_used()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:

                            bools,current_ele_set_end_time=check_allowable(refrence_time,elements,Class_Data,ele,line)

                            if bools:
                                
                                ele.set_end_time(current_ele_set_end_time)
                                ele.set_used(1)
                                ele.set_line_name(line)
                                non_prior_list1.append(ele)
                                remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                                refrence_time=refrence_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time


                non_prior_list1=non_prior_list3+non_prior_list1
                non_prior_list1,remaining_time=stretch_allowable_two_args(non_prior_list1,non_prior_list1,flag_object,elements,remaining_time,dates,line)
                # print(f"Fut non pror recs {len(future_non_prior_records)}")
                
                for ele in future_data:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0 and ele.get_used()==0:
                        if ele.get_weight_limit()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:
                            ele.set_used(1)
                            ele.set_line_name(line)
                            non_prior_list2.append(ele)
                            remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                            # print(remaining_time)

                non_prior_list2,remaining_time=stretch_allowable_two_args(non_prior_list2,non_prior_list2,flag_object,elements,remaining_time,dates,line)
                # if still time is remaining  but tempahin has not been able to be alocated then 
                # shifting time and making sure the remaining tempahin will be allocated

                non_prior_list=non_prior_list+non_prior_list1+non_prior_list2



                for ele in non_prior_list:
                    ele.set_used(1)
                    ele.set_line_name(line)
        
                non_prior_list=fuction_to_allocate(remaining_time,future_with_today,non_prior_list,elements,Class_Data,flag_object,dates,future_with_today_special,line)
                
                
                
                today_usable_future_last_records.reverse()

                # print(f'today_usable future_first_records :{today_usable_future_first_records}')

                non_pror=non_prior_list
                if MC_short_check:
                    OP=[]
                    GP=non_pror
                    for ele in GP:
                        if ele.get_syouhin_name()=='ｲﾄｳIK-NT(H)' or ele.get_syouhin_name()=='ﾊﾟﾈﾘ-PV(13)':
                            non_pror.remove(ele)
                            OP.append(ele)

                    today_usable_future_first_records=today_usable_future_first_records+OP


                all_records=today_usable_future_first_records+non_pror+today_usable_future_last_records




            elif len(today_first_records)==0 and len(today_last_records)!=0:
                print("first Zero last non Zero")
                
                MC_short_check=False
                remaining_time=total_time#-total_time_for_today_last_records

                today_non_prior_list=[]
                still_not_allocated=[]
                refrence_time=remaining_time
                for ele in non_priority_record:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:

                        if ele.get_weight_limit()==1:
                            bools,current_ele_set_end_time=check_allowable(remaining_time,elements,Class_Data,ele,line)
                            if bools:
                                ele.set_end_time(current_ele_set_end_time)
                                ele.set_used(1)
                                ele.set_line_name(line)
                                today_non_prior_list.append(ele)                     
                                remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                            else:
                                still_not_allocated.append(ele)

                        else:
                            today_non_prior_list.append(ele)
                            ele.set_used(1)
                            ele.set_line_name(line)
                            remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time


                today_non_prior_list,remaining_time=stretch_allowable_two_args(today_non_prior_list,today_non_prior_list,flag_object,elements,remaining_time,dates,line)


                # future_last_record_lists_along_with_today

                today_with_future_last_records=[]
                if today_last_records[0].get_yousoka()=='高' or today_last_records[0].get_yousoka()=='準高':
                    today_with_future_last_records=Record_finder.last_record_finder(future_with_today,types='高')
                    jyunko_dekiru=Record_finder.last_record_finder(future_with_today,types='準高')

                    for ele in jyunko_dekiru:
                        today_with_future_last_records.append(ele)

                elif today_last_records[0].get_yousoka()=='低':
                    today_with_future_last_records=Record_finder.last_record_finder(future_with_today,types='低')
                

                elif today_last_records[0].get_Allergy()=='B' or today_last_records[0].get_MOS()=='〇':
                    today_with_future_last_records=Record_finder.last_record_finder_two(future_with_today,types='B')
                    arerukon_records=Record_finder.last_record_finder_four_MOS(future_with_today,types='〇')
                    arerukon_re=arerukon_records
                    nep=[]
                    # shifting record with name ﾊｲDXﾌｱﾂﾄ(H) to last
                    for tokui_rec in arerukon_re:
                        if tokui_rec.get_syouhin_name()=='ﾊｲDXﾌｱﾂﾄ(H)':
                            nep.append(tokui_rec)
                            arerukon_records.remove(tokui_rec)
                    for ele in nep:
                        arerukon_records.append(ele)

                    for ele in arerukon_records:
                        today_with_future_last_records.append(ele)

                elif today_last_records[0].get_saishu_gentei()=='〇':
                    today_with_future_last_records=Record_finder.last_record_finder_three(future_with_today,types='〇')

                
                today_last_records.clear()
                for ele in today_with_future_last_records:
                    if ele not in today_last_records:
                        if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                            today_last_records.append(ele)
                            remaining_time= remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time



                today_last_records,remaining_time=stretch_allowable_two_args(today_last_records,today_last_records,flag_object,elements,remaining_time,dates,line)


                future_first_records=[]
                dummy=[]
                for ele in future_data:
                    if ele.get_firsts()==1:
                        dummy.append(ele)
                
                top_rec=None
                if len(dummy)>0:
                    top_record_nouki_copy=dummy[0].get_nouki_copy()
                    top_rec=dummy[0]
                    for ele in dummy:
                        print(ele.get_syouhin_name())
                        if ele.get_nouki_copy()==top_record_nouki_copy and ele.get_syouhin_name().startswith('MCｼｮｰﾄ'):
                            top_rec=ele
                
                    # print(ele.get_syouhin_name())  
                

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
                        mc_record=Record_finder.first_record_finder_renzoku(future_data1,type1='ｲﾄｳIK-NT(H)', type2='ﾊﾟﾈﾘ-PV(13)')
                        for ele in mc_record:
                            future_first_records.append(ele)
                        MC_short_check=True

                    elif top_rec.get_bikou()=='初回限定':
                        future_first_records=Record_finder.first_record_finder_two(future_data,types='初回限定')

                    elif top_rec.get_bikou()=='副原料無添' or top_rec.get_syouhin_name()=='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)':
                        future_first_records=Record_finder.first_record_finder_two(future_data,types='副原料無添')
                        rem_renzoku_record=Record_finder.first_record_finder_three(future_data,types='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)')
                        for re in rem_renzoku_record:
                            if re not in future_first_records:
                                future_first_records.append(re)



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


                future_first_records_list,remaining_time=stretch_allowable_two_args(future_first_records_list,future_first_records_list,flag_object,elements,remaining_time,dates,line)

                # # getting future non prior lists
                # future_non_prior_records=[]

                # for fut_rec in future_data:
                #     if fut_rec.get_used()==0 and fut_rec.get_firsts()==0 and fut_rec.get_lasts()==0 and fut_rec.get_last_first()==0:
                #         future_non_prior_records.append(fut_rec)


                


                future_non_prior_list=[]
                future_non_prior_list1=[]
                future_non_prior_list2=[]

                all_data=still_not_allocated
                for ele in future_with_today:
                    if ele not in all_data:
                        all_data.append(ele)
                
                for ele in future_with_today_special:
                    if ele not in all_data:
                        all_data.append(ele)

                for i in range(len(all_data)):
                    

                    for ele in all_data:
                        if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                            if ele.get_weight_limit()==1 and ele.get_used()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:

                                bools,current_ele_set_end_time=check_allowable(refrence_time,elements,Class_Data,ele,line)
                                if bools:
                                    ele.set_end_time(current_ele_set_end_time)
                                    ele.set_used(1)
                                    ele.set_line_name(line)
                                    future_non_prior_list2.append(ele)
                                    remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                                    refrence_time=refrence_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                        


                    for ele in all_data:
                        if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0 and ele.get_used()==0:
                            if ele.get_weight_limit()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:
                                future_non_prior_list2.append(ele)
                                ele.set_used(1)
                                ele.set_line_name(line)
                                remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                                refrence_time=refrence_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                        
                                break







                for ele in future_data:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        if ele.get_weight_limit()==1 and ele.get_used()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:
                        
                            #
                            bools,current_ele_set_end_time=check_allowable(refrence_time,elements,Class_Data,ele,line)
                            if bools:
                                ele.set_end_time(current_ele_set_end_time)
                                ele.set_used(1)
                                ele.set_line_name(line)
                                future_non_prior_list.append(ele)
                                remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                                refrence_time=refrence_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                            

                future_non_prior_list=future_non_prior_list2+future_non_prior_list



                future_non_prior_list,remaining_time=stretch_allowable_two_args(future_non_prior_list,future_non_prior_list,flag_object,elements,remaining_time,dates,line)

                
                for ele in future_data:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0 and ele.get_used()==0:
                        if ele.get_weight_limit()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:
                            future_non_prior_list1.append(ele)
                            ele.set_used(1)
                            ele.set_line_name(line)
                            remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time


                future_non_prior_list1,remaining_time=stretch_allowable_two_args(future_non_prior_list1,future_non_prior_list1,flag_object,elements,remaining_time,dates,line)
                

                future_non_prior_list=future_non_prior_list+future_non_prior_list1
                today_last_records.reverse()

                for ele in today_non_prior_list:
                    ele.set_used(1)
                    ele.set_line_name(line)

                today_non_prior_list=fuction_to_allocate(remaining_time,future_with_today,today_non_prior_list,elements,Class_Data,flag_object,dates,future_with_today_special,line)

                non_pror=today_non_prior_list+future_non_prior_list
                if MC_short_check:
                    OP=[]
                    GP=non_pror
                    for ele in GP:
                        if ele.get_syouhin_name()=='ｲﾄｳIK-NT(H)' or ele.get_syouhin_name()=='ﾊﾟﾈﾘ-PV(13)':
                            non_pror.remove(ele)
                            OP.append(ele)

                    future_first_records_list=future_first_records_list+OP



                all_records=future_first_records_list+non_pror+today_last_records


                
                    
            elif len(today_first_records)!=0 and len(today_last_records)==0:

                print("First non zero last zero")
                MC_short_check=False

                remaining_time=total_time#-total_time_for_today_first_record
                # refrence_time=remaining_time
                still_not_allocated=[]
                today_non_prior_list=[]
                for ele in non_priority_record:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        if ele.get_weight_limit()==1:
                            bools,current_ele_set_end_time=check_allowable(remaining_time,elements,Class_Data,ele,line)

                            if bools:
                                ele.set_end_time(current_ele_set_end_time)
                                ele.set_used(1)
                                ele.set_line_name(line)
                                today_non_prior_list.append(ele)
                                remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                            else:
                                still_not_allocated.append(ele)

            
                        else:

                            today_non_prior_list.append(ele)
                            ele.set_used(1)
                            ele.set_line_name(line)
                            remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

            


                today_non_prior_list,remaining_time=stretch_allowable_two_args(today_non_prior_list,today_non_prior_list,flag_object,elements,remaining_time,dates,line)

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
                    mc_record=Record_finder.first_record_finder_renzoku(future_with_today1,type1='ｲﾄｳIK-NT(H)', type2='ﾊﾟﾈﾘ-PV(13)')
                    for ele in mc_record:
                        today_with_future_first_records.append(ele)
                    MC_short_check=True

                elif today_first_records[0].get_bikou()=='初回限定':
                    today_with_future_first_records=Record_finder.first_record_finder_two(future_with_today,types='初回限定')

                elif today_first_records[0].get_bikou()=='副原料無添' or today_first_records[0].get_syouhin_name()=='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)':
                    today_with_future_first_records=Record_finder.first_record_finder_two(future_with_today,types='副原料無添')
                    rem_renzoku_record=Record_finder.first_record_finder_three(future_with_today,types='ﾌﾟﾚﾐｱﾑｼﾖ-ﾄ-CF(S)')
                    for re in rem_renzoku_record:
                        if re not in today_with_future_first_records:
                            today_with_future_first_records.append(re)
                    

                today_first_records.clear()
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

                today_first_records,remaining_time=stretch_allowable_two_args(today_first_records,today_first_records,flag_object,elements,remaining_time,dates,line)
                refrence_time=remaining_time

                dummy2=[]
                for ele in future_data:
                    if ele.get_lasts()==1 or ele.get_last_first()==1:
                        dummy2.append(ele)

                top_rec2=None
                if len(dummy2)>0:
                    top_rec2=dummy2[0]
                future_last_records=[]
                if top_rec2!=None:
                    if top_rec2.get_yousoka()=='高' or top_rec2.get_yousoka()=='準高':
                        future_last_records=Record_finder.last_record_finder(future_data,types='高')
                        jyunko_dekiru=Record_finder.last_record_finder(future_data,types='準高')

                        for ele in jyunko_dekiru:
                            future_last_records.append(ele)

                    elif top_rec2.get_yousoka()=='低':
                        future_last_records=Record_finder.last_record_finder(future_data,types='低')
                

                    elif top_rec2.get_Allergy()=='B' or top_rec2.get_MOS()=='〇':
                        future_last_records=Record_finder.last_record_finder_two(future_data,types='B')
                        arerukon_records=Record_finder.last_record_finder_four_MOS(future_data,types='〇')
                        
                        arerukon_re=arerukon_records
                        nep=[]
                        # shifting record with name ﾊｲDXﾌｱﾂﾄ(H) to last
                        for tokui_rec in arerukon_re:
                            if tokui_rec.get_syouhin_name()=='ﾊｲDXﾌｱﾂﾄ(H)':
                                nep.append(tokui_rec)
                                arerukon_records.remove(tokui_rec)
                        for ele in nep:
                            arerukon_records.append(ele)


                        for ele in arerukon_records:
                            future_last_records.append(ele)

                    elif top_rec2.get_saishu_gentei()=='〇':
                        future_last_records=Record_finder.last_record_finder_three(future_data,types='〇')

                
                future_last_records_list=[]

                for ele in future_last_records:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        future_last_records_list.append(ele)
                        remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time


                future_last_records_list,remaining_time=stretch_allowable_two_args(future_last_records_list,future_last_records_list,flag_object,elements,remaining_time,dates,line)
                # getting future non prior lists


                future_non_prior_list=[]
                future_non_prior_list1=[]
                future_non_prior_list2=[]

                all_data=still_not_allocated
                for ele in future_with_today:
                    if ele not in all_data:
                        all_data.append(ele)
                
                for ele in future_with_today_special:
                    if ele not in all_data:
                        all_data.append(ele)

                for i in range(len(all_data)):
                    
                    for ele in all_data:
                        # print(ele.get_ticket_no())
                        if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                            if ele.get_weight_limit()==1 and ele.get_used()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:

                            
                                bools,current_ele_set_end_time=check_allowable(refrence_time,elements,Class_Data,ele,line)
                                # print("IN")
                                if bools:
                                    ele.set_end_time(current_ele_set_end_time)
                                    ele.set_used(1)
                                    ele.set_line_name(line)
                                    future_non_prior_list2.append(ele)
                                    remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                                    refrence_time=refrence_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                        

                    for ele in all_data:
                        if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0 and ele.get_used()==0:
                            if ele.get_weight_limit()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:
                                future_non_prior_list2.append(ele)
                                ele.set_used(1)
                                ele.set_line_name(line)
                                remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                                refrence_time=refrence_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                                break

                for ele in future_data:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0:
                        if ele.get_weight_limit()==1 and ele.get_used()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:

                        
                            bools,current_ele_set_end_time=check_allowable(refrence_time,elements,Class_Data,ele,line)
                            # print("IN")
                            if bools:
                                ele.set_end_time(current_ele_set_end_time)
                                ele.set_used(1)
                                ele.set_line_name(line)
                                future_non_prior_list.append(ele)
                                remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                                refrence_time=refrence_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time
                        
                        

                future_non_prior_list=future_non_prior_list2+future_non_prior_list
                future_non_prior_list,remaining_time=stretch_allowable_two_args(future_non_prior_list,future_non_prior_list,flag_object,elements,remaining_time,dates,line)


                for ele in future_data:
                    if remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time>0 and ele.get_used()==0:
                        if ele.get_weight_limit()==0 and ele.get_firsts()==0 and ele.get_lasts()==0 and ele.get_last_first()==0:
                            ele.set_used(1)
                            ele.set_line_name(line)
                            future_non_prior_list1.append(ele)
                            remaining_time=remaining_time-ele.get_cleaning_time()-getattr(ele,f'get_{line}_time_taken')()-cleaning_time

                future_non_prior_list1,remaining_time=stretch_allowable_two_args(future_non_prior_list1,future_non_prior_list1,flag_object,elements,remaining_time,dates,line)
                future_non_prior_list=future_non_prior_list+future_non_prior_list1

                

                future_last_records_list.reverse()
                # for ele in future_last_records_list:
                #     print(ele.get_ticket_no())
                
                for ele in today_non_prior_list:
                    ele.set_used(1)
                    ele.set_line_name(line)

                today_non_prior_list=fuction_to_allocate(remaining_time,future_with_today,today_non_prior_list,elements,Class_Data,flag_object,dates,future_with_today_special,line)

                non_pror=today_non_prior_list+future_non_prior_list
                if MC_short_check:
                    OP=[]
                    GP=non_pror
                    for ele in GP:
                        if ele.get_syouhin_name()=='ｲﾄｳIK-NT(H)' or ele.get_syouhin_name()=='ﾊﾟﾈﾘ-PV(13)':
                            non_pror.remove(ele)
                            OP.append(ele)

                    today_first_records=today_first_records+OP


                all_records=today_first_records+non_pror+future_last_records_list

            task_wise_icrement=0
            # i=0
            # prev_record=None
            # # only_one_time_count=0
            # for record in all_records:
                

            #     if i==0:
            #         before_time=allowable_start_time
            #         saturday_special_time1=before_time
            #         saturday_special_time2=before_time
            #     else:
            #         before_time=allowable_start_time+timedelta(minutes=cleaning_time)+timedelta(minutes=prev_record.get_cleaning_time())

            #     if record.get_st_time()!=None:
            #         before_time=record.get_st_time()
                

            #     if (elements.day_name()=='Sunday' or elements.day_name()=='Saturday') and (saturday_special_time1-timedelta(minutes=cleaning_time)<=elements+timedelta(hours=17) and saturday_special_time2>elements+timedelta(hours=17)):
            #         before_time=before_time+timedelta(minutes=20)

            #     if (elements.day_name()=='Sunday' or elements.day_name()=='Saturday') and (saturday_special_time1-timedelta(minutes=cleaning_time)<=elements+timedelta(hours=11) and saturday_special_time2>elements+timedelta(hours=11)):
            #         before_time=before_time+timedelta(minutes=20)

                
            #     allowable_start_time=before_time+timedelta(minutes=getattr(record,f'get_{line}_time_taken')())
            #     record.set_slot(before_time,allowable_start_time)
            #     task_wise_icrement+=1
            #     record.set_jyounban(task_wise_icrement)

            #     record.set_seisanbi(start_time)
            #     record.set_used(1)
            #     record.set_end_time(allowable_start_time)


            #     prev_record=record

            #     saturday_special_time1=before_time
            #     saturday_special_time2=allowable_start_time

            
            #     i+=1


            i = 0
            prev_record = None
            for record in all_records:
                before_before_time = allowable_start_time

                if i == 0:
                    before_time = allowable_start_time
                    saturday_special_time1 = before_time
                    saturday_special_time2 = before_time + timedelta(minutes=getattr(record,f'get_{line}_time_taken')())
                else:
                    before_time = allowable_start_time + timedelta(minutes=cleaning_time) + timedelta(minutes=prev_record.get_cleaning_time())

                # Adjust before_time if there is a nitrigen gas transition
                if prev_record is not None:
                    prev_nitrogen_gas = prev_record.get_nitrogen_gas()
                    current_nitrogen_gas = record.get_nitrogen_gas()
                    # Check for transition between '〇' and blank (empty string)
                    if (prev_nitrogen_gas == '〇' and current_nitrogen_gas != '〇') or (prev_nitrogen_gas != '〇' and current_nitrogen_gas == '〇'):
                        # Add extra 10 minutes for the nitrigen gas transition
                        before_time += timedelta(minutes=10)
                        # Adjust remaining_time accordingly if needed
                        # If you manage remaining_time in this loop, uncomment the following line:
                        # remaining_time -= 10

                if record.get_st_time() is not None:
                    before_time = record.get_st_time()

                # Adjust for Saturday and Sunday special times
                if (elements.day_name() == 'Sunday' or elements.day_name() == 'Saturday') and \
                (saturday_special_time1 - timedelta(minutes=cleaning_time) <= elements + timedelta(hours=17) and saturday_special_time2 > elements + timedelta(hours=17)):
                    before_time += timedelta(minutes=20)

                if (elements.day_name() == 'Sunday' or elements.day_name() == 'Saturday') and \
                (saturday_special_time1 - timedelta(minutes=cleaning_time) <= elements + timedelta(hours=11) and saturday_special_time2 > elements + timedelta(hours=11)):
                    before_time += timedelta(minutes=20)

                # Calculate the allowable start time for the current record
                allowable_start_time = before_time + timedelta(minutes=getattr(record,f'get_{line}_time_taken')())

                # Account for the added 10 minutes in allowable_start_time
                difference_of_time = allowable_start_time - before_before_time

                # Adjust for breaks if necessary
                for index, (duration, break_start) in enumerate(zip(line_break_duration_list, line_break_start)):
                    if before_before_time < break_start and allowable_start_time > break_start:
                        time_to_reach_break = break_start - before_time
                        time_to_reach_break_mins = time_to_reach_break.total_seconds() / 60
                        before_time = break_start + timedelta(minutes=duration)
                        allowable_start_time = before_time + difference_of_time

                # Check if the allowable_start_time exceeds the day's working hours
                if allowable_start_time > elements + timedelta(hours=23):
                    break  # Exit the loop if the schedule exceeds the working day

                # Set the scheduling details for the record
                record.set_slot(before_time, allowable_start_time)
                task_wise_icrement += 1
                record.set_jyounban(task_wise_icrement)

                record.set_seisanbi(start_time)
                record.set_used(1)
                record.set_line_name(line)
                record.set_end_time(allowable_start_time)

                # Update previous record and special times for the next iteration
                prev_record = record
                saturday_special_time1 = before_time
                saturday_special_time2 = allowable_start_time

                i += 1

            
            prev_Date=elements

            unused_records=[ele for ele in all_records if ele.get_seisanbi()==None]
            all_records=[ele for ele in all_records if ele not in unused_records]
            unused_records=[ele.set_used(0) for ele in unused_records]



            prev_Date=elements

            
            for ele in all_records:  
                final_df=final_df.append({'品目コード':ele.get_syouhin_code(),
                                        '品名':ele.get_syouhin_name(),
                                        'ライン':ele.get_line(),
                                        '荷姿':ele.get_packaging(),
                                        # 'ライン名':ele.get_line_name(),
                                        '入目':ele.get_iri_me(),
                                        '流速':ele.get_ryousoku(),
                                        'テンパリング':ele.get_tenpahin(),
                                        '沃素価':ele.get_yousoka(),
                                        'KI製品':ele.get_KI(),
                                        '初回限定':ele.get_syoukai_gentei(),
                                        '最終限定':ele.get_saishu_gentei(),
                                        'リパック':ele.get_stretch(),
                                        '予定数量(㎏)':ele.get_yotei_syourou(),
                                        '納期':ele.get_nouki(),
                                        'チケットＮＯ':ele.get_ticket_no(),
                                        '備考':ele.get_bikou(),
                                        '生産日':ele.get_seisanbi(),
                                        '順番':ele.get_jyounban(),
                                        'slot':ele.get_slot(),
                                        'nouki_copy':ele.get_nouki_copy().date(),
                                        '窒素ガス' :ele.get_nitrogen_gas(),
                                        'MO-7S配合': ele.get_MOS(),
                                        'アレルゲン':ele.get_Allergy(),
                                        'SP_time_taken':ele.get_SP_time_taken(),
                                        'SV_time_taken':ele.get_SV_time_taken(),
                                        'SP_rate/hr':ele.get_sp_rate(),
                                        'SV_rate/hr':ele.get_sv_rate(),
                                        'start':ele.get_start_date_time(),
                                        'end':ele.get_end_date_time(),
                                        'day':ele.get_end_date_time().day_name()

                    },
                    ignore_index=True)


    return final_df,Class_Data,remaining_time


def unused_dataframe(Class_Data,non_final_df,abc):
    non_final_df["nouki_copy"]=None
    for ele in Class_Data:

        if ele.get_used()==0:
            non_final_df=non_final_df.append({'品目コード':ele.get_syouhin_code(),
                                            '品名':ele.get_syouhin_name(),
                                            'ライン':ele.get_line(),
                                            # 'ライン名':ele.get_line_name(),
                                            '入目':ele.get_iri_me(),
                                            '流速':ele.get_ryousoku(),
                                            'テンパリング':ele.get_tenpahin(),
                                            '沃素価':ele.get_yousoka(),
                                            'KI':ele.get_KI(),
                                            '初回限定':ele.get_syoukai_gentei(),
                                            '最終限定':ele.get_saishu_gentei(),
                                            'リパック':ele.get_stretch(),
                                            '予定数量(㎏)':ele.get_yotei_syourou(),
                                            '納期':ele.get_nouki(),
                                            'チケットＮＯ':ele.get_ticket_no(),
                                            '備考':ele.get_bikou(),
                                            '生産日':ele.get_seisanbi(),
                                            '順番':ele.get_jyounban(),
                                            'slot':ele.get_slot(),
                                            'nouki_copy':ele.get_nouki_copy()
                                            },
                                            ignore_index=True)

    non_final_df.to_csv(f"remaining_{abc}.csv",encoding="utf-8_sig",index=False)
    
