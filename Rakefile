gem 'rake', '>= 0.7.3'
require 'rake'

TEST_DIR = './test'

def test_dir &block
  Dir.chdir(TEST_DIR) do
    block.call
  end
end

desc "Run unit tests"
task :tests do |t|
  sh './alltests.py'
end

desc "Run code coverage"
task :coverage do |t|
  Rake::Task['coverage:main'].invoke
  Rake::Task['coverage:clean'].invoke
end

namespace "coverage" do
  task :main do |t|
    sh 'coverage -e -x ./alltests.py'
    sh 'coverage -r -m'
  end
  
  task :clean do
    File.delete '.coverage' if File.exists? '.coverage'
  end
  
  task :html do |t|
    Rake::Task['coverage:main'].invoke
    sh 'coverage -b -d ./test/html'
    sh 'open ./test/html/index.html'
    Rake::Task['coverage:clean'].invoke
  end
  
end
