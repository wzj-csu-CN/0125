import numpy as np
import pandas as pd
#import scipy.stats
import random
import math
from time import time
names = locals()
#from ast import literal_eval

#数据导入
df_area = pd.read_csv('/public/home/hpc204212088/connected_vehicle/xin3/shortest_path/area.csv')

list_county = list(df_area['c_id'])
df_density = pd.read_csv('/public/home/hpc204212088/connected_vehicle/xin3/picture/vehicle_density.csv')
df_ppl_code=pd.read_csv(r'/public/home/hpc204212088/connected_vehicle/xin3/people_code/people_code.csv')

df_ppl_wai = df_ppl_code[df_ppl_code['c_id1']!=df_ppl_code['c_id2']].reset_index(drop=True)
list_id = list()
list_c = list()
for i in range(len(df_ppl_wai)):
	for j in range(df_ppl_wai['id_start'][i],df_ppl_wai['id_end'][i]+1):
		list_id.append(j)
		list_c.append(df_ppl_wai['c_id1'][i])
	print(i)
df_hibernat = pd.DataFrame()
df_hibernat['id'] = list_id
df_hibernat['c_id'] = list_c

df_ppl_nei = df_ppl_code[df_ppl_code['c_id1']==df_ppl_code['c_id2']].reset_index(drop=True)
list_id = list()
list_c = list()
for i in range(len(df_ppl_nei)):
	for j in range(df_ppl_nei['id_start'][i],df_ppl_nei['id_end'][i]+1):
		list_id.append(j)
		list_c.append(df_ppl_nei['c_id1'][i])
	print(i)
df_hibernat_nei = pd.DataFrame()
df_hibernat_nei['id'] = list_id
df_hibernat_nei['c_id'] = list_c

# df_mid = pd.read_csv('/public/home/hpc204212088/connected_vehicle/xin3/friends_network/m_id/m=0.3.csv')
# df_hibernat = df_hibernat[df_hibernat['id'].isin(set(df_mid['ppl']))]
# df_hibernat_nei = df_hibernat_nei[df_hibernat_nei['id'].isin(set(df_mid['ppl']))]

#df_location = pd.read_csv('/t3/connected_vehicle/xin/coordinates_location/location_complete.csv')

#求<k>
def average_k(N,county):
	area = df_area[df_area['c_id']==county]['land'].reset_index(drop=True)[0]
	k = (N*math.pi*300*300)/area
	return(k)

#求新时间窗新增感染的人数

def spread(N,S,I,k):
	list_new_i = list()
	for a in range(10):
		new_i = k * S * I / N 
		if (new_i>S):
			new_i = S
		integer = int(new_i)
		decimal = new_i - integer
		d_choice = np.random.choice([0,1],p=[1-decimal,decimal])
		new_i = integer + d_choice	
		I = I + new_i
		S = S - new_i

		list_new_i.append(new_i)
	return (list_new_i)

sigma = 10
m = 1
#初始化

ill_num = 0
seed_ppl = 15936554
sl=1





list_ill_people_num = list()
list_ill_ppl = list([seed_ppl])


df_wai_stop = pd.DataFrame(columns=['id','c_id'])
new_ill = pd.DataFrame(columns=['id','c_id'])
for tw in range(1,144*28+1):
	list_ill_ppl_fz = list_ill_ppl.copy()
	start_time = time()
	TW = tw
	list_new_ill = list()	
	df_ill_new =pd.DataFrame()
	df_ill_new['ill'] = list([0])*10	
	#print(time()-start_time,1)

	df_move_wai_all = pd.read_csv('/public/home/hpc204212088/connected_vehicle/xin3/move_vehicle/m='+ str(m) +'/external_move_id_sigma' + str(sigma) + '/' + str(tw) + '.csv')
	#print(time()-start_time,2)

	df_hibernat = df_hibernat[~df_hibernat['id'].isin(set(df_move_wai_all['id']))]

	df_hibernat_stop = df_wai_stop[~df_wai_stop['id'].isin(set(df_move_wai_all['id']))]

	df_hibernat = pd.concat([df_hibernat,df_hibernat_stop])

	df_wai_stop = df_move_wai_all.copy()

	new_ill=pd.concat([new_ill,df_hibernat_nei[df_hibernat_nei['id'].isin(set(list_ill_ppl))]])
	df_hibernat_nei = df_hibernat_nei[~df_hibernat_nei['id'].isin(set(list_ill_ppl))]

	df_move_all = pd.concat([df_move_wai_all,df_hibernat])
	#print(time()-start_time,3)

	df_ill = pd.concat([new_ill,df_move_all[df_move_all['id'].isin(set(list_ill_ppl))]])
	df_noill = pd.concat([df_hibernat_nei,df_move_all[~df_move_all['id'].isin(set(list_ill_ppl))]])
	list_ill_county = list(set(df_ill['c_id']))

	for county in list_ill_county:
		county = int(county)

		df_ill_tw = df_ill[df_ill['c_id']==county] 
		df_noill_tw = df_noill[df_noill['c_id']==county] 

		list_I = list(df_ill_tw['id'])
		list_S = list(df_noill_tw['id'])
		I = len(set(list_I))
		S = len(set(list_S))
		N = I + S

		if(I>0):
			k = average_k(N,county)
			list_new = spread(N,S,I,k)#新增感染人数

			df_ill_new['new'] = list_new
			df_ill_new['ill'] = df_ill_new['ill'] + df_ill_new['new']
			new_i = df_ill_new['new'].sum()	
			if (new_i>0):
				for ill_id in random.sample(list_S,new_i):
					list_ill_ppl.append(ill_id)#添加这个county新增感染的人
					list_new_ill.append(ill_id)		
	for n in list(df_ill_new['ill']):
		ill_num = ill_num+n
		list_ill_people_num.append(ill_num)  #总感染人数
	print(TW,ill_num,time()-start_time)


	#导出
	df_csv = pd.DataFrame()
	df_csv['ill_num'] = list_ill_people_num
	df_csv.to_csv('/public/home/hpc204212088/connected_vehicle/xin3/wifi_result1/m='+str(m)+'/'+str(sigma)+'/all_vehicle_seed'+str(sl)+'.csv',index=False)

	chu_df = pd.DataFrame(columns=['ppl'])
	chu_df['ppl'] = list(set(list_ill_ppl).difference(set(list_ill_ppl_fz)))  # 输出这个时间窗相对于上个时间窗多出来的感染的人
	chu_df.to_csv('/public/home/hpc204212088/connected_vehicle/xin3/wifi_result1/m='+str(m)+'/10/simulation'+str(sl)+'/'+str(tw) + '.csv', index=None)





