  select u.username,u.id,
  u.fname || ' ' || u.lname as fullname, 
  x.prop_value as lastlogin,
  :companyid as companyid,
  u.username as actions from ign_users u
inner join ign_user_rl rl
on rl.user_id = u.id
inner join ign_roles r
on r.id = rl.role_id
and r.role_name = :companyid
left join ign_user_ex x
on x.id = u.id
and x.prop_name = 'lastlogin'

order by username