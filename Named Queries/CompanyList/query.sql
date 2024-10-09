

SELECT 
companyid,company_name,count(rl.*) as users,mqtt_topic,mqtt_topic as edit 
FROM company c
inner join ign_roles r
on r.role_name = c.mqtt_topic
left join ign_user_rl rl
on rl.role_id = r.id
group by companyid,c.mqtt_topic
order by c.company_name