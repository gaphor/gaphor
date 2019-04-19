cat .gitignore | while read dir; do
  rm -rf $dir
done
