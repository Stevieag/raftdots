from collections import defaultdict
import re
from datetime import datetime, date, timedelta

def parse_line(line):
    parts = line.strip().split(',')
    if len(parts) >= 4:
        full_name = parts[0].strip('"')
        date_string = parts[3].strip('"')
        match = re.search(r'(\d{4}-\d{2}-\d{2})', date_string)
        if match:
            release_date = match.group(1)
            return full_name, release_date
    return None, None

def get_group_names(full_name):
    parts = full_name.split('-')
    if len(parts) <= 2:
        return full_name, full_name
    
    # Main group is always the first two parts
    main_group = '-'.join(parts[:2])
    
    # Sub-group is everything up to the last part (which is often a unique identifier)
    sub_group = '-'.join(parts[:-1])
    
    return main_group, sub_group

def calculate_age(release_date):
    release_date = datetime.strptime(release_date, "%Y-%m-%d").date()
    current_date = date.today()
    age_days = (current_date - release_date).days
    age_hours = age_days * 24
    return age_days, age_hours

def process_data(data):
    grouped_deployments = defaultdict(lambda: defaultdict(list))
    group_dates = defaultdict(lambda: defaultdict(list))

    for line in data.strip().split('\n'):
        full_name, release_date = parse_line(line)
        if full_name and release_date:
            age_days, age_hours = calculate_age(release_date)
            if age_days > 7:  # Only process deployments older than 7 days
                main_group, sub_group = get_group_names(full_name)
                grouped_deployments[main_group][sub_group].append((full_name, (age_days, age_hours), release_date))
                group_dates[main_group][sub_group].append(release_date)

    # Remove main groups with only one sub-group
    grouped_deployments = {main: sub for main, sub in grouped_deployments.items() if len(sub) > 1}
    group_dates = {main: sub for main, sub in group_dates.items() if len(sub) > 1}

    #print("Grouped Deployments (older than 7 days, with multiple sub-groups, excluding latest):")
    for main_group, sub_groups in grouped_deployments.items():
        non_empty_sub_groups = False
        main_group_output = f"\n{main_group}\n"
        sub_group_output = ""

        for sub_group, deployments in sub_groups.items():
            sorted_deployments = sorted(deployments, key=lambda x: x[2], reverse=True)
            
            # Start from the second deployment if there's more than one
            start_index = 1 if len(sorted_deployments) > 1 else 0
            
            if len(sorted_deployments[start_index:]) > 0:
                non_empty_sub_groups = True
                sub_group_output += f" {sub_group}\n"
                
                for deployment, (age_days, age_hours), _ in sorted_deployments[start_index:]:
                    if deployment != sub_group:
                        sub_group_output += f"  {deployment} (Age: {age_days} days)\n"
                sub_group_output += "\n"

        if non_empty_sub_groups:
#            print(main_group_output + sub_group_output)
            print( sub_group_output)

    total_main_groups = sum(1 for sub_groups in grouped_deployments.values() if any(len(deployments) > 1 for deployments in sub_groups.values()))
    total_sub_groups = sum(sum(1 for deployments in sub_groups.values() if len(deployments) > 1) for sub_groups in grouped_deployments.values())
    total_deployments = sum(sum(max(0, len(deployments) - 1) for deployments in sub_groups.values()) for sub_groups in grouped_deployments.values())

    #print(f"\nTotal number of main groups (with multiple non-empty sub-groups): {total_main_groups}")
    #print(f"Total number of non-empty sub-groups: {total_sub_groups}")
    #print(f"Total number of deployments (older than 7 days, excluding latest): {total_deployments}")

    total_main_groups = len(grouped_deployments)
    total_sub_groups = sum(len(sub_groups) for sub_groups in grouped_deployments.values())
    total_deployments = sum(sum(len(deployments) - 1 for deployments in sub_groups.values()) for sub_groups in grouped_deployments.values())

    #print(f"\nTotal number of main groups (with multiple sub-groups): {total_main_groups}")
    #print(f"Total number of sub-groups: {total_sub_groups}")
    #print(f"Total number of deployments (older than 7 days, excluding latest): {total_deployments}")

# Sample data
sample_data = '''
"name","namespace","revision","updated","status","chart","app_version"
"ap-validation-prototype","default","45","2024-09-02 11:37:22.717403877 +0000 UTC","deployed","ap-validation-prototype-0.1.0","1.0"
"billing-service","default","23","2024-09-02 11:24:43.140318069 +0000 UTC","deployed","billing-service-0.1.0","1.0"
"capybara-server","default","7","2024-03-12 20:21:24.626855352 +0000 UTC","deployed","capybara-server-0.1.0","1.0"
"cert-manager","default","2","2023-08-31 09:05:09.329524 +0100 BST","deployed","cert-manager-v1.12.3","v1.12.3"
"classification","ml","2","2024-09-17 12:06:01.395420214 +0000 UTC","failed","email-ml-0.0.1","1.0"
"clf","ml","1","2024-09-17 17:08:02.827610988 +0000 UTC","deployed","email-ml-0.0.1","1.0"
"cw-data-store-service","default","37","2024-09-03 14:12:26.961742248 +0000 UTC","deployed","cw-data-store-service-0.1.0","1.16.0"
"dagster","dagster","382","2024-09-17 20:56:26.977534445 +0000 UTC","deployed","dagster-1.6.3","1.6.3"
"dagster-oauth2-proxy","dagster","6","2024-01-03 18:05:42.93637 +0000 UTC","deployed","oauth2-proxy-6.23.1","7.5.1"
"dataset-evaluator","default","90","2024-08-30 12:21:21.262560827 +0000 UTC","deployed","dataset-evaluator-0.1.0","1.0"
"dataset-evaluator-oauth2-proxy","default","2","2024-02-15 14:25:01.190726 +0000 UTC","deployed","oauth2-proxy-6.23.1","7.5.1"
"edi-file-gen","default","21","2024-09-19 06:45:06.459003263 +0000 UTC","deployed","edi-file-gen-0.1.0","1.0"
"edi-file-gen-cus-4","default","1","2024-09-02 07:25:10.422533566 +0000 UTC","deployed","edi-file-gen-0.1.0","1.0"
"edi-file-gen-cus-mgd4xf","default","1","2024-08-27 20:36:09.719461372 +0000 UTC","deployed","edi-file-gen-0.1.0","1.0"
"edi-processing","default","46","2024-08-14 15:48:43.870636569 +0000 UTC","deployed","edi-processing-0.1.0","1.0"
"elasticsearch-ml","ml","6","2024-02-06 16:13:12.241974657 +0000 UTC","deployed","elasticsearch-19.5.15","8.6.2"
"email-classification","default","89","2024-09-19 14:58:01.597872037 +0000 UTC","deployed","email-classification-0.0.1","1.0"
"email-eop","default","55","2024-09-19 14:58:04.222559456 +0000 UTC","deployed","email-eop-0.0.1","1.0"
"email-head","default","53","2024-09-19 14:57:12.075759 +0000 UTC","deployed","email-head-0.0.1","1.0"
"email-ner","default","90","2024-09-19 14:57:28.665933117 +0000 UTC","deployed","email-ner-0.0.1","1.0"
"fields-extraction","ml","3","2024-09-02 16:59:20.236191159 +0000 UTC","deployed","fields-extraction-0.0.1","1.0"
"file-data-processor","default","21","2024-09-02 10:15:13.411655051 +0000 UTC","deployed","file-data-processor-0.1.0","1.0"
"gitlab-runner","gitlab-runner","31","2024-05-09 14:46:23.630855 +0100 BST","deployed","gitlab-runner-0.61.0","16.8.0"
"gitlab-slack","default","57","2024-09-11 08:17:04.370321874 +0000 UTC","deployed","gitlab-slack-0.1.0","1.0"
"grafana","monitoring","11","2023-12-05 01:25:22.953245782 +0000 UTC","deployed","grafana-9.6.3","10.2.2"
"head","ml","1","2024-09-16 17:19:29.82019243 +0000 UTC","failed","email-ml-0.0.1","1.0"
"ingress","default","16","2024-08-01 18:16:36.528239 +0100 BST","deployed","ingress-nginx-4.11.1","1.11.1"
"keda","default","3","2024-04-02 12:34:12.467948 +0100 BST","deployed","keda-2.11.2","2.11.2"
"kube-state-metrics","monitoring","1","2023-07-27 16:24:38.888559714 +0200 +0200","deployed","kube-state-metrics-5.10.1","2.9.2"
"line-detection","ml","52","2024-09-17 17:29:42.024664071 +0000 UTC","deployed","line-detection-0.1.0","1.0"
"linkerd-control-plane","linkerd","2","2024-06-24 23:43:29.609104922 +0100 BST","deployed","linkerd-control-plane-2024.6.3","edge-24.6.3"
"linkerd-crds","linkerd","1","2024-06-21 14:51:25.734519022 +0100 BST","deployed","linkerd-crds-2024.6.2",""
"linkerd-jaeger","linkerd-jaeger","2","2024-06-24 23:46:11.439879892 +0100 BST","deployed","linkerd-jaeger-2024.6.3","edge-24.6.3"
"linkerd-viz","linkerd-viz","3","2024-06-24 23:45:28.697972801 +0100 BST","deployed","linkerd-viz-2024.6.3","edge-24.6.3"
"locust-layoutlm-server","monitoring","1","2023-09-08 19:35:37.79209 +0530 +0530","deployed","locust-0.31.4","2.15.1"
"matomo","default","2","2024-06-27 17:00:15.906604 +0100 BST","deployed","matomo-0.1.0","1.0"
"matomo-mysql","default","1","2020-05-13 18:02:44.286959 +0100 BST","deployed","mysql-6.13.0","8.0.20"
"ner","ml","1","2024-09-17 17:11:04.072384308 +0000 UTC","deployed","email-ml-0.0.1","1.0"
"ocr-clustering","ml","12","2024-09-12 13:57:08.403989211 +0000 UTC","deployed","ocr-clustering-0.1.0","1.0"
"pack-splicing-and-classification","default","23","2024-09-16 15:27:01.817392141 +0000 UTC","deployed","pack-splicing-and-classification-0.1.0","1.0"
"payments-staging-c75q0p","default","3","2023-01-19 12:55:56.752144295 +0000 UTC","deployed","vector-payment-integrations-0.1.0","0.1"
"prometheus","monitoring","8","2024-01-23 14:27:19.366059145 +0000 UTC","deployed","prometheus-15.12.0","2.36.2"
"pulsar-operator","pulsar","1","2023-11-21 13:05:45.839105088 +0000 UTC","deployed","pulsar-operator-0.17.8","0.17.8"
"quotes-rates","default","210","2024-09-02 11:29:36.835479031 +0000 UTC","deployed","quotes-rates-0.1.0","1.0"
"raft-cluster-kafka-ui","kafka","2","2023-09-18 10:34:19.423784 +0100 BST","deployed","kafka-ui-0.7.5","v0.7.1"
"raft-masterdata","default","27","2024-09-18 09:36:38.733967986 +0000 UTC","deployed","raft-masterdata-0.1.0","1.16.0"
"raft-partners","default","40","2024-07-31 13:45:37.188912702 +0000 UTC","deployed","raft-partners-0.1.0","1.16.0"
"raft-ship-ext-consumer","default","153","2024-09-03 12:24:56.820407091 +0000 UTC","deployed","raft-ship-ext-consumer-0.1.0","1.16.0"
"raft-ship-ext-producer","default","130","2024-09-03 12:25:13.358690853 +0000 UTC","deployed","raft-ship-ext-producer-0.1.0","1.16.0"
"raft-ship-ext-rabbitmq","default","115","2024-09-03 12:24:50.654726705 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"raftbot","default","17","2024-07-19 14:15:54.22276632 +0000 UTC","deployed","raftbot-0.1.0","1.0"
"redis-cache","default","3","2023-10-17 18:20:21.889844 +0100 BST","deployed","redis-17.14.2","7.0.12"
"ref-apps2-276-loo-xl2f43-db","default","1","2024-03-19 11:57:38.457436229 +0000 UTC","deployed","postgresql-11.7.0","14.4.0"
"ref-apps2-276-loo-xl2f43-redis","default","4","2024-03-20 08:34:49.624950003 +0000 UTC","deployed","redis-17.15.6","7.2.0"
"ref-enblr-164-car-ghb99a-db","default","1","2024-04-04 14:21:07.341200689 +0000 UTC","deployed","postgresql-11.7.0","14.4.0"
"ref-omn-1912-ekjwfw","default","3","2024-09-19 13:36:53.974462769 +0000 UTC","deployed","vector-cargowise-reference-lookup-0.1.0","1.0"
"ref-omn-1912-ekjwfw-db","default","1","2024-09-11 15:40:06.562604265 +0000 UTC","deployed","postgresql-11.7.0","14.4.0"
"ref-omn-1912-ekjwfw-redis","default","3","2024-09-19 13:36:49.44758379 +0000 UTC","deployed","redis-17.15.6","7.2.0"
"response-parser","default","29","2024-09-02 12:36:32.513506201 +0000 UTC","deployed","response-parser-0.1.0","1.0"
"rq-exporter","monitoring","2","2023-04-18 14:35:21.798979793 +0200 +0200","deployed","rq-exporter-0.1.0","2.0.0"
"rq-exporter","default","1","2023-07-31 12:11:46.528885 +0100 BST","deployed","rq-exporter-0.1.0","2.0.0"
"search-engine","default","309","2024-09-19 11:05:28.861455297 +0000 UTC","deployed","search-engine-0.1.0","1.0"
"search-engine-elastic","default","6","2024-01-18 17:25:15.568258679 +0000 UTC","deployed","elasticsearch-19.3.0","8.4.1"
"sentry","sentry","11","2024-01-23 21:33:22.585473763 +0000 UTC","deployed","sentry-20.5.3","23.8.0"
"shadow-model-store-server","default","14","2024-09-05 09:59:24.974386655 +0000 UTC","deployed","shadow-model-store-server-0.1.0","1.0"
"staging-rabbitmq","default","5824","2024-03-15 21:12:15.880196582 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"summary-view","default","15","2024-09-02 11:38:34.44459598 +0000 UTC","deployed","summary-view-0.1.0","1.0"
"text-translation","default","11","2024-09-02 10:18:33.999573779 +0000 UTC","deployed","text-translation-0.1.0","1.0"
"timescale-db","default","3","2024-05-17 15:20:54.157376 +0100 BST","deployed","timescaledb-single-0.33.1",""
"vector-address-extraction","default","7","2023-05-19 15:53:46.430757479 +0000 UTC","deployed","vector-address-extraction-0.1.0","1.0"
"vector-address-parsing","default","6","2023-06-14 12:34:45.104433639 +0000 UTC","deployed","vector-address-parsing-0.1.0","1.0"
"vector-audit-service","default","148","2024-09-02 10:45:31.99393492 +0000 UTC","deployed","vector-audit-service-0.1.0","1.0"
"vector-backend","default","6488","2024-09-20 09:38:00.647361238 +0000 UTC","deployed","vector-backend-0.1.0","1.0"
"vector-backend-bl-dhtr3n","default","4","2024-09-20 07:15:47.606761469 +0000 UTC","deployed","vector-backend-0.1.0","1.0"
"vector-backend-bl-dhtr3n-audit","default","4","2024-09-20 07:15:27.478970367 +0000 UTC","deployed","vector-audit-service-0.1.0","1.0"
"vector-backend-bl-dhtr3n-db","default","1","2024-09-19 14:46:06.428336083 +0000 UTC","deployed","postgresql-12.12.10","15.4.0"
"vector-backend-bl-dhtr3n-frontend","default","4","2024-09-20 07:18:22.325549813 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-backend-bl-dhtr3n-rabbitmq","default","4","2024-09-20 07:15:09.572911675 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"vector-backend-bl-dhtr3n-redis","default","4","2024-09-20 07:15:20.31921877 +0000 UTC","deployed","redis-17.15.6","7.2.0"
"vector-backend-cu-ajt3xw","default","8","2024-09-20 09:03:39.808172349 +0000 UTC","deployed","vector-backend-0.1.0","1.0"
"vector-backend-cu-ajt3xw-audit","default","8","2024-09-20 09:03:24.214616436 +0000 UTC","deployed","vector-audit-service-0.1.0","1.0"
"vector-backend-cu-ajt3xw-db","default","1","2024-09-17 12:55:53.500110119 +0000 UTC","deployed","postgresql-12.12.10","15.4.0"
"vector-backend-cu-ajt3xw-frontend","default","8","2024-09-20 09:04:15.313888825 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-backend-cu-ajt3xw-rabbitmq","default","8","2024-09-20 09:03:09.160644795 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"vector-backend-cu-ajt3xw-redis","default","8","2024-09-20 09:03:16.351765241 +0000 UTC","deployed","redis-17.15.6","7.2.0"
"vector-backend-do-6i1gtt","default","1","2024-09-18 16:07:34.500699249 +0000 UTC","deployed","vector-backend-0.1.0","1.0"
"vector-backend-do-6i1gtt-audit","default","1","2024-09-18 16:07:22.820124596 +0000 UTC","deployed","vector-audit-service-0.1.0","1.0"
"vector-backend-do-6i1gtt-db","default","1","2024-09-18 15:55:07.907812805 +0000 UTC","deployed","postgresql-12.12.10","15.4.0"
"vector-backend-do-6i1gtt-frontend","default","1","2024-09-18 16:10:26.653826172 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-backend-do-6i1gtt-rabbitmq","default","1","2024-09-18 16:05:53.569781585 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"vector-backend-do-6i1gtt-redis","default","1","2024-09-18 16:06:43.997844007 +0000 UTC","deployed","redis-17.15.6","7.2.0"
"vector-backend-ed-2opmwn","default","23","2024-09-19 17:04:53.480541982 +0000 UTC","deployed","vector-backend-0.1.0","1.0"
"vector-backend-ed-2opmwn-audit","default","23","2024-09-19 17:04:39.33426131 +0000 UTC","deployed","vector-audit-service-0.1.0","1.0"
"vector-backend-ed-2opmwn-db","default","1","2024-09-04 17:38:46.999896574 +0000 UTC","deployed","postgresql-12.12.10","15.4.0"
"vector-backend-ed-2opmwn-frontend","default","16","2024-09-19 17:06:43.127453888 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-backend-ed-2opmwn-rabbitmq","default","23","2024-09-19 17:04:25.976887491 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"vector-backend-ed-2opmwn-redis","default","23","2024-09-19 17:04:33.742323133 +0000 UTC","deployed","redis-17.15.6","7.2.0"
"vector-backend-fi-9q5ljb","default","4","2024-09-19 15:48:02.301115526 +0000 UTC","deployed","vector-backend-0.1.0","1.0"
"vector-backend-fi-9q5ljb-audit","default","4","2024-09-19 15:47:48.80341043 +0000 UTC","deployed","vector-audit-service-0.1.0","1.0"
"vector-backend-fi-9q5ljb-db","default","1","2024-09-18 13:55:57.771412774 +0000 UTC","deployed","postgresql-12.12.10","15.4.0"
"vector-backend-fi-9q5ljb-frontend","default","4","2024-09-19 15:50:13.680470116 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-backend-fi-9q5ljb-rabbitmq","default","4","2024-09-19 15:47:36.539705492 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"vector-backend-fi-9q5ljb-redis","default","4","2024-09-19 15:47:43.56991845 +0000 UTC","deployed","redis-17.15.6","7.2.0"
"vector-backend-fi-gz2u39","default","1","2024-09-18 15:20:17.647369118 +0000 UTC","deployed","vector-backend-0.1.0","1.0"
"vector-backend-fi-gz2u39-audit","default","1","2024-09-18 15:20:05.541060898 +0000 UTC","deployed","vector-audit-service-0.1.0","1.0"
"vector-backend-fi-gz2u39-db","default","1","2024-09-18 15:09:13.583758738 +0000 UTC","deployed","postgresql-12.12.10","15.4.0"
"vector-backend-fi-gz2u39-frontend","default","1","2024-09-18 15:22:22.498179737 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-backend-fi-gz2u39-rabbitmq","default","1","2024-09-18 15:18:34.217847471 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"vector-backend-fi-gz2u39-redis","default","1","2024-09-18 15:19:26.774226606 +0000 UTC","deployed","redis-17.15.6","7.2.0"
"vector-backend-fi-lam6t2","default","3","2024-09-18 07:31:19.855808127 +0000 UTC","deployed","vector-backend-0.1.0","1.0"
"vector-backend-fi-lam6t2-audit","default","3","2024-09-18 07:31:05.376107319 +0000 UTC","deployed","vector-audit-service-0.1.0","1.0"
"vector-backend-fi-lam6t2-db","default","1","2024-09-18 06:42:59.036967018 +0000 UTC","deployed","postgresql-12.12.10","15.4.0"
"vector-backend-fi-lam6t2-frontend","default","3","2024-09-18 07:33:16.102989672 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-backend-fi-lam6t2-rabbitmq","default","3","2024-09-18 07:30:52.123963776 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"vector-backend-fi-lam6t2-redis","default","3","2024-09-18 07:31:00.080531369 +0000 UTC","deployed","redis-17.15.6","7.2.0"
"vector-backend-fi-p1ujym","default","1","2024-09-20 08:36:18.382709903 +0000 UTC","deployed","vector-backend-0.1.0","1.0"
"vector-backend-fi-p1ujym-audit","default","1","2024-09-20 08:36:06.562525366 +0000 UTC","deployed","vector-audit-service-0.1.0","1.0"
"vector-backend-fi-p1ujym-db","default","1","2024-09-20 08:23:34.719154395 +0000 UTC","deployed","postgresql-12.12.10","15.4.0"
"vector-backend-fi-p1ujym-frontend","default","1","2024-09-20 08:38:36.817227082 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-backend-fi-p1ujym-rabbitmq","default","1","2024-09-20 08:34:37.419897833 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"vector-backend-fi-p1ujym-redis","default","1","2024-09-20 08:35:23.735268682 +0000 UTC","deployed","redis-17.15.6","7.2.0"
"vector-backend-om-eqpcna","default","26","2024-09-19 16:03:49.91076911 +0000 UTC","deployed","vector-backend-0.1.0","1.0"
"vector-backend-om-eqpcna-audit","default","26","2024-09-19 16:03:36.386376535 +0000 UTC","deployed","vector-audit-service-0.1.0","1.0"
"vector-backend-om-eqpcna-db","default","1","2024-08-21 13:40:10.149253834 +0000 UTC","deployed","postgresql-12.12.10","15.4.0"
"vector-backend-om-eqpcna-frontend","default","25","2024-09-19 16:06:30.478239391 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-backend-om-eqpcna-rabbitmq","default","26","2024-09-19 16:03:20.466268488 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"vector-backend-om-eqpcna-redis","default","26","2024-09-19 16:03:30.270606455 +0000 UTC","deployed","redis-17.15.6","7.2.0"
"vector-backend-om-y1u7k0","default","2","2024-09-19 16:28:25.739413876 +0000 UTC","deployed","vector-backend-0.1.0","1.0"
"vector-backend-om-y1u7k0-audit","default","2","2024-09-19 16:28:13.878756729 +0000 UTC","deployed","vector-audit-service-0.1.0","1.0"
"vector-backend-om-y1u7k0-db","default","1","2024-09-19 11:54:41.922753531 +0000 UTC","deployed","postgresql-12.12.10","15.4.0"
"vector-backend-om-y1u7k0-frontend","default","2","2024-09-19 16:30:38.515133379 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-backend-om-y1u7k0-rabbitmq","default","2","2024-09-19 16:28:01.901585186 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"vector-backend-om-y1u7k0-redis","default","2","2024-09-19 16:28:08.927903465 +0000 UTC","deployed","redis-17.15.6","7.2.0"
"vector-cargowise-9npzgn","default","4","2024-09-19 10:31:12.457639596 +0000 UTC","deployed","vector-cargowise-ap-processing-0.1.0","1.0"
"vector-cargowise-9npzgn-db","default","1","2024-09-13 09:48:42.542436471 +0000 UTC","deployed","postgresql-11.7.0","14.4.0"
"vector-cargowise-9npzgn-rabbitmq","default","4","2024-09-19 10:31:07.976077067 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"vector-cargowise-ap-processing","default","191","2024-09-19 13:09:17.781987932 +0000 UTC","deployed","vector-cargowise-ap-processing-0.1.0","1.0"
"vector-cargowise-b89zaf","default","2","2024-09-19 13:38:26.831394612 +0000 UTC","deployed","vector-cargowise-ap-processing-0.1.0","1.0"
"vector-cargowise-b89zaf-db","default","1","2024-09-19 12:19:27.650370943 +0000 UTC","deployed","postgresql-11.7.0","14.4.0"
"vector-cargowise-b89zaf-rabbitmq","default","2","2024-09-19 13:38:21.571257874 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"vector-cargowise-bynngf","default","2","2024-09-06 13:03:08.606910066 +0000 UTC","deployed","vector-cargowise-ap-processing-0.1.0","1.0"
"vector-cargowise-bynngf-db","default","1","2024-09-06 11:30:05.289563534 +0000 UTC","deployed","postgresql-11.7.0","14.4.0"
"vector-cargowise-bynngf-rabbitmq","default","4","2024-09-06 13:03:03.86041659 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"vector-cargowise-reference-lookup","default","158","2024-09-20 09:42:36.426495266 +0000 UTC","deployed","vector-cargowise-reference-lookup-0.1.0","1.0"
"vector-clamav","default","1","2023-05-04 17:21:59.461018656 +0000 UTC","deployed","vector-clamav-0.1.0","1.16.0"
"vector-classify","default","407","2024-09-02 10:46:18.838072956 +0000 UTC","deployed","vector-classify-0.1.0","1.0"
"vector-config-man-6cipoo-db","default","1","2024-05-03 14:37:19.617507435 +0000 UTC","deployed","postgresql-11.6.6","14.3.0"
"vector-config-man-b17vew-db","default","2","2024-04-02 16:16:59.863250966 +0000 UTC","deployed","postgresql-11.6.6","14.3.0"
"vector-config-man-fdhooh-db","default","1","2024-05-24 14:39:16.674849393 +0000 UTC","deployed","postgresql-11.6.6","14.3.0"
"vector-config-man-q2x9bk-db","default","1","2024-07-29 18:47:36.535927638 +0000 UTC","deployed","postgresql-11.6.6","14.3.0"
"vector-config-man-yskd4w-db","default","1","2024-04-16 14:36:33.026643976 +0000 UTC","deployed","postgresql-11.6.6","14.3.0"
"vector-config-manager","default","1289","2024-09-19 14:53:25.644939276 +0000 UTC","deployed","vector-config-manager-0.1.0","1.0"
"vector-dbt-docs","default","45","2024-09-19 15:04:38.326469993 +0000 UTC","deployed","vector-dbt-docs-0.1.0","1.16.0"
"vector-document-extraction","default","125","2024-08-12 12:35:14.952096478 +0000 UTC","deployed","vector-document-extraction-0.1.0","1.0"
"vector-email-processing","default","48","2023-11-21 21:31:53.223594227 +0000 UTC","deployed","vector-email-processing-0.1.0","1.0"
"vector-email-serv-6eyf2u","default","1","2024-08-02 09:21:45.628886535 +0000 UTC","deployed","vector-email-service-0.1.0","1.0"
"vector-email-serv-6eyf2u-be","default","1","2024-08-02 09:22:18.611452294 +0000 UTC","deployed","vector-backend-0.1.0","1.0"
"vector-email-serv-6eyf2u-db-be","default","1","2024-08-02 09:11:09.776164292 +0000 UTC","deployed","postgresql-11.7.0","14.4.0"
"vector-email-serv-6eyf2u-db-email","default","1","2024-08-02 08:19:51.797691146 +0000 UTC","deployed","postgresql-11.7.0","14.4.0"
"vector-email-serv-6eyf2u-e","default","2","2024-08-02 08:42:04.488966767 +0000 UTC","deployed","vector-email-service-0.1.0","1.0"
"vector-email-serv-6eyf2u-fe","default","1","2024-08-02 09:23:55.448300769 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-email-serv-6eyf2u-rabbitmq","default","1","2024-08-02 09:20:28.114621566 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"vector-email-serv-6eyf2u-redis","default","3","2024-08-02 09:20:20.581639178 +0000 UTC","deployed","redis-17.15.6","7.2.0"
"vector-email-service","default","176","2024-09-19 10:25:47.820435953 +0000 UTC","deployed","vector-email-service-0.1.0","1.0"
"vector-entity-classifier","default","4","2020-09-10 10:15:43.098629526 +0000 UTC","deployed","vector-entity-classifier-0.1.0","1.0"
"vector-etron","default","75","2024-09-16 19:52:33.064778873 +0000 UTC","deployed","vector-etron-0.1.0","1.0"
"vector-excel-extraction","default","26","2024-09-20 09:21:21.090724607 +0000 UTC","deployed","vector-excel-extraction-0.1.0","1.0"
"vector-extract","default","1256","2024-09-19 17:17:02.985559976 +0000 UTC","deployed","vector-extract-0.1.0","1.0"
"vector-extract-cr-wctu2b","default","1","2024-09-18 09:26:15.402933804 +0000 UTC","pending-install","vector-extract-0.1.0","1.0"
"vector-extract-cr-wctu2b-db","default","1","2024-09-18 09:21:27.37057785 +0000 UTC","deployed","postgresql-11.6.6","14.3.0"
"vector-extract-cr-wctu2b-elasticsearch","default","1","2024-09-18 09:23:08.224700644 +0000 UTC","deployed","elasticsearch-19.5.15","8.6.2"
"vector-extract-cr-wctu2b-redis","default","1","2024-09-18 09:25:30.923042499 +0000 UTC","deployed","redis-17.10.2","7.0.11"
"vector-extract-fe-8xat2s-db","default","1","2024-06-04 10:45:21.565415034 +0000 UTC","deployed","postgresql-11.6.6","14.3.0"
"vector-extract-fe-8xat2s-elasticsearch","default","1","2024-06-04 10:47:18.053185854 +0000 UTC","deployed","elasticsearch-19.5.15","8.6.2"
"vector-extract-fe-8xat2s-redis","default","1","2024-06-04 10:49:36.848643248 +0000 UTC","deployed","redis-17.10.2","7.0.11"
"vector-frontend","default","4185","2024-09-20 05:31:25.420350186 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-frontend-b-y22np5","default","2","2024-09-10 17:41:14.765782029 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-frontend-b-y22np5-unleash-proxy","default","2","2024-09-10 17:41:26.590109896 +0000 UTC","deployed","unleash-proxy-0.1.0","1.0"
"vector-frontend-b-yk7ei2","default","2","2024-09-16 13:14:35.155886903 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-frontend-b-yk7ei2-unleash-proxy","default","2","2024-09-16 13:14:43.848464051 +0000 UTC","deployed","unleash-proxy-0.1.0","1.0"
"vector-frontend-c-h657qs","default","6","2024-09-19 08:47:20.804529589 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-frontend-c-h657qs-unleash-proxy","default","6","2024-09-19 08:47:27.693842771 +0000 UTC","deployed","unleash-proxy-0.1.0","1.0"
"vector-frontend-c-j16620","default","4","2024-09-17 13:27:04.711714439 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-frontend-c-j16620-unleash-proxy","default","4","2024-09-17 13:27:11.416692761 +0000 UTC","deployed","unleash-proxy-0.1.0","1.0"
"vector-frontend-e-bhzsfs","default","7","2024-09-13 12:47:56.528402549 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-frontend-e-bhzsfs-unleash-proxy","default","7","2024-09-13 12:48:05.691117371 +0000 UTC","deployed","unleash-proxy-0.1.0","1.0"
"vector-frontend-e-e6jtw7","default","3","2024-08-29 13:01:07.147264557 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-frontend-e-e6jtw7-unleash-proxy","default","3","2024-08-29 13:01:16.881367232 +0000 UTC","deployed","unleash-proxy-0.1.0","1.0"
"vector-frontend-f-wtxal5","default","1","2024-09-04 04:48:19.611216019 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-frontend-f-wtxal5-unleash-proxy","default","1","2024-09-04 04:48:25.891552483 +0000 UTC","deployed","unleash-proxy-0.1.0","1.0"
"vector-frontend-o-5rq7xe","default","9","2024-09-19 16:21:34.102388191 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-frontend-o-5rq7xe-unleash-proxy","default","9","2024-09-19 16:21:40.696934608 +0000 UTC","deployed","unleash-proxy-0.1.0","1.0"
"vector-frontend-o-aswky7","default","2","2024-09-16 13:36:24.625127736 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-frontend-o-aswky7-unleash-proxy","default","2","2024-09-16 13:36:33.461522563 +0000 UTC","deployed","unleash-proxy-0.1.0","1.0"
"vector-frontend-o-c26d0r","default","1","2024-09-11 08:10:52.464262506 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-frontend-o-c26d0r-unleash-proxy","default","1","2024-09-11 08:11:00.352138036 +0000 UTC","deployed","unleash-proxy-0.1.0","1.0"
"vector-frontend-o-l6hych","default","1","2024-08-30 10:46:14.043250248 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-frontend-o-l6hych-unleash-proxy","default","1","2024-08-30 10:46:22.289412858 +0000 UTC","deployed","unleash-proxy-0.1.0","1.0"
"vector-frontend-o-m05sln","default","5","2024-09-19 13:19:14.452608313 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"vector-frontend-o-m05sln-unleash-proxy","default","5","2024-09-19 13:19:23.426188825 +0000 UTC","deployed","unleash-proxy-0.1.0","1.0"
"vector-frontend-unleash-proxy","default","2822","2024-09-20 05:31:46.033441742 +0000 UTC","deployed","unleash-proxy-0.1.0","1.0"
"vector-hoppscotch","default","1","2023-03-30 09:25:22.350825833 +0000 UTC","deployed","vector-hoppscotch-0.1.0","1.16.0"
"vector-issuer-recognition","default","132","2024-09-06 16:45:59.849018386 +0000 UTC","deployed","vector-issuer-recognition-0.1.0","1.0"
"vector-large-models-client","default","154","2024-09-20 08:25:02.510877764 +0000 UTC","deployed","vector-large-models-client-0.1.0","1.0"
"vector-metabase","default","7","2024-08-12 11:39:58.63092946 +0000 UTC","deployed","vector-metabase-0.1.0","1.16.0"
"vector-netchb","default","3","2022-03-22 13:49:03.141395718 +0000 UTC","deployed","vector-netchb-0.1.0","1.0"
"vector-ocr-manage-0yf4r2","default","3","2024-09-18 13:11:34.723095544 +0000 UTC","deployed","vector-ocr-manager-0.1.0","1.0"
"vector-ocr-manager","default","379","2024-09-19 13:49:52.26445905 +0000 UTC","deployed","vector-ocr-manager-0.1.0","1.0"
"vector-ocr-manager-reader","default","180","2024-09-19 13:49:59.041267722 +0000 UTC","deployed","vector-ocr-manager-0.1.0","1.0"
"vector-payment-integrations","default","75","2024-07-19 14:15:27.962253219 +0000 UTC","deployed","vector-payment-integrations-0.1.0","0.1"
"vector-ports-service","default","16","2022-10-03 08:41:25.347817244 +0000 UTC","deployed","vector-ports-service-0.1.0","1.16.0"
"vector-rules","default","17","2024-05-03 08:54:57.461760468 +0000 UTC","deployed","vector-rules-0.1.0","1.0"
"vector-sentence-tagger","default","5","2020-09-17 18:01:11.384928992 +0000 UTC","deployed","vector-sentence-tagger-0.1.0","1.0"
"vector-splice","default","240","2024-09-16 19:43:36.96343894 +0000 UTC","deployed","vector-splice-0.1.0","1.0"
"vector-standardize","default","480","2024-09-19 10:12:49.29584136 +0000 UTC","deployed","vector-standardize-0.1.0","1.0"
"vector-website","default","42","2021-07-02 11:08:42.785630886 +0000 UTC","deployed","vector-website-0.1.0","1.0"
"workflow-builder","default","183","2024-09-19 17:18:00.004725916 +0000 UTC","deployed","workflow-builder-0.1.0","1.0"
"workflow-builder-fwk-543","default","5","2024-09-20 06:12:56.126041327 +0000 UTC","deployed","workflow-builder-0.1.0","1.0"
"workflow-builder-fwk-543-audit","default","5","2024-09-20 06:12:25.688209757 +0000 UTC","deployed","vector-audit-service-0.1.0","1.0"
"workflow-builder-fwk-543-be","default","5","2024-09-20 06:15:08.008644482 +0000 UTC","deployed","vector-backend-0.1.0","1.0"
"workflow-builder-fwk-543-db-be","default","1","2024-09-18 09:01:45.005817178 +0000 UTC","deployed","postgresql-12.12.10","15.4.0"
"workflow-builder-fwk-543-fe","default","5","2024-09-20 06:15:32.133802647 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"workflow-builder-fwk-543-rabbitmq","default","5","2024-09-20 06:12:20.570011487 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"workflow-builder-fwk-543-redis","default","5","2024-09-20 06:12:13.334163422 +0000 UTC","deployed","redis-17.15.6","7.2.0"
"workflow-builder-k9rao4-db-be","default","1","2024-06-10 09:27:19.973629906 +0000 UTC","deployed","postgresql-12.12.10","15.4.0"
"workflow-builder-rfyap8","default","4","2024-09-16 10:59:55.57393681 +0000 UTC","deployed","workflow-builder-0.1.0","1.0"
"workflow-builder-rfyap8-audit","default","4","2024-09-16 10:59:25.717848306 +0000 UTC","deployed","vector-audit-service-0.1.0","1.0"
"workflow-builder-rfyap8-be","default","4","2024-09-16 11:00:10.666439591 +0000 UTC","deployed","vector-backend-0.1.0","1.0"
"workflow-builder-rfyap8-db-be","default","1","2024-09-06 08:10:49.296804576 +0000 UTC","deployed","postgresql-12.12.10","15.4.0"
"workflow-builder-rfyap8-fe","default","4","2024-09-16 11:01:49.003028428 +0000 UTC","deployed","vector-frontend-0.1.0","1.0"
"workflow-builder-rfyap8-rabbitmq","default","4","2024-09-16 10:59:20.917281893 +0000 UTC","deployed","rabbitmq-12.0.13","3.12.3"
"workflow-builder-rfyap8-redis","default","4","2024-09-16 10:59:13.548307038 +0000 UTC","deployed","redis-17.15.6","7.2.0"
"workflow-builder-venmdf-db-be","default","1","2024-09-18 08:25:00.867763334 +0000 UTC","deployed","postgresql-12.12.10","15.4.0"
'''

if __name__ == "__main__":
    process_data(sample_data)











