def new_test()
  assert(create_memo()) == db.dated.find() #everytime there should be one more element inside
  assert(make run) == db.dated.find() #date should sort by date
  assert(humanize_arrow_date("2017-11-6") == Today
  assert(humanize_arrow_date("2017-11-7") == Tomorrow
  assert(humanize_arrow_date("2017-11-5") == Yesterday
