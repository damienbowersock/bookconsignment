import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  rootDir: '.',
  moduleFileExtensions: ['ts', 'js', 'json'],
  testRegex: '.*\\.spec\\.ts$',
  transform: {
    '^.+\\.(t|j)s$': 'ts-jest'
  },
  moduleNameMapper: {
    '^@bookconsign\\/schemas\\/(.*)$': '<rootDir>/../../packages/schemas/src/$1',
    '^@bookconsign\\/lib\\/(.*)$': '<rootDir>/../../packages/lib/src/$1'
  },
  coverageDirectory: '../../coverage/apps-api'
};

export default config;
