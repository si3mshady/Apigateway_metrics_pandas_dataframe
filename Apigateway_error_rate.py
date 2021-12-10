import boto3, datetime
import pandas as pd 

NAMESPACE  = 'AWS/ApiGateway'

metric_names = ['Count', '5XXError','4XXError']

api_counts , errors_5XX, errors_4XX = [], [], []
api_counts_name, errors_5XX_name, errors_4XX_name = [], [], []


def get_yesterdays_date():
    return datetime.datetime.today()-datetime.timedelta(days=1)

def get_start_time(day):
    return day.replace(second=0,minute=0,hour=0).timestamp()

def get_end_time(day):
    return day.replace(second=59, minute=59,hour=23).timestamp()

def fetch_all_api_names():
    apigw = boto3.client('apigateway' , region_name='us-east-1')    
    return [name.get('name') for name in apigw.get_rest_apis(limit=20).get('items') ]  



def get_api_count(api_name,metric_name='Count'):
    cw  = boto3.client('cloudwatch', region_name='us-east-1')
    day = get_yesterdays_date()
    response =cw.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'test',
                'MetricStat': {
                    'Metric': {
                        'Namespace': NAMESPACE,
                        'MetricName': metric_name,
                        'Dimensions': [
                            {
                                'Name': 'ApiName',
                                'Value': api_name
                            },
                        ]
                    },
                    'Period': 86400,
                    'Stat': 'Sum'
                },
            
                'Label': f'Api_{metric_name}',
                'ReturnData': True
            
            },
        ],
        StartTime=get_start_time(day),
        EndTime=get_end_time(day)    
    )
  
    return response['MetricDataResults'][0]['Values']

def make_dataframes():
    for metric in metric_names:
        for api in fetch_all_api_names():
            val = get_api_count(api, metric)
            if len(val) > 0:
                match metric:
                    case "Count":
                        api_counts.append(val[0])
                        api_counts_name.append(api)
                    case "5XXError":
                        errors_5XX.append(val[0])
                        errors_5XX_name.append(api)                    
                    case "4XXError":
                        errors_4XX.append(val[0])
                        errors_4XX_name.append(api)

        
    print_dataframe({"Counts": api_counts, "Name": api_counts_name})
    print_dataframe({"5XXErrors":errors_5XX,"Name": errors_5XX_name} )
    print_dataframe({"4XXErrors":errors_4XX, "Name": errors_4XX_name })

def print_dataframe(object):
    print(pd.DataFrame(object))


make_dataframes()


#Elliott Arnold
#Gather apigateway cloudwatch metrics into dataframes for analysis 
#12-9-21, 7-11
#part1
