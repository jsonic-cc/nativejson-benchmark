#include "../test.h"

#include "json.h"

namespace {

void GenStat(Stat& stat, const json::Document& value) {
    switch (value.type) {
        case json::Type::Array:
            ++stat.arrayCount;
            stat.elementCount += value.array.size();
            for (const json::Document& element : value.array)
                GenStat(stat, element);
            break;

        case json::Type::Object:
            ++stat.objectCount;
            stat.memberCount += value.object.size();
            stat.stringCount += value.object.size();
            for (const auto& member : value.object) {
                stat.stringLength += member.first.size();
                GenStat(stat, member.second);
            }
            break;

        case json::Type::Number:
            ++stat.numberCount;
            break;

        case json::Type::String:
            ++stat.stringCount;
            stat.stringLength += value.string.size();
            break;

        case json::Type::Boolean:
            if (value.boolean)
                ++stat.trueCount;
            else
                ++stat.falseCount;
            break;

        case json::Type::Null:
            ++stat.nullCount;
            break;
    }
}

void Stringify(std::string& output, const json::Document& value) {
    switch (value.type) {
        case json::Type::Array:
            output.push_back('[');
            for (std::size_t i = 0; i < value.array.size(); ++i) {
                if (i != 0)
                    output.push_back(',');
                Stringify(output, value.array[i]);
            }
            output.push_back(']');
            break;

        case json::Type::Object:
            output.push_back('{');
            for (std::size_t i = 0; i < value.object.size(); ++i) {
                if (i != 0)
                    output.push_back(',');
                output.push_back('"');
                json::Document::append_escaped_string(output, value.object[i].first);
                output += "\":";
                Stringify(output, value.object[i].second);
            }
            output.push_back('}');
            break;

        case json::Type::String:
            output.push_back('"');
            json::Document::append_escaped_string(output, value.string);
            output.push_back('"');
            break;

        default:
            output += value.dump(0);
            break;
    }
}

class JsonicParseResult : public ParseResultBase {
public:
    json::Document root;
};

class JsonicStringResult : public StringResultBase {
public:
    virtual const char* c_str() const override { return value.c_str(); }

    std::string value;
};

class JsonicTest : public TestBase {
public:
#if TEST_INFO
    virtual const char* GetName() const override { return "Jsonic++ (C++17)"; }
    virtual const char* GetFilename() const override { return __FILE__; }
#endif

#if TEST_PARSE
    virtual ParseResultBase* Parse(const char* input, size_t length) const override {
        JsonicParseResult* result = new JsonicParseResult;
        std::string error;
        if (!json::Document::parse(std::string_view(input, length), result->root, error)) {
            delete result;
            return 0;
        }
        return result;
    }
#endif

#if TEST_STRINGIFY
    virtual StringResultBase* Stringify(const ParseResultBase* parseResult) const override {
        const JsonicParseResult* result = static_cast<const JsonicParseResult*>(parseResult);
        JsonicStringResult* string = new JsonicStringResult;
        string->value.reserve(256);
        ::Stringify(string->value, result->root);
        return string;
    }
#endif

#if TEST_PRETTIFY
    virtual StringResultBase* Prettify(const ParseResultBase* parseResult) const override {
        const JsonicParseResult* result = static_cast<const JsonicParseResult*>(parseResult);
        JsonicStringResult* string = new JsonicStringResult;
        string->value = result->root.dump(4);
        return string;
    }
#endif

#if TEST_STATISTICS
    virtual bool Statistics(const ParseResultBase* parseResult, Stat* stat) const override {
        const JsonicParseResult* result = static_cast<const JsonicParseResult*>(parseResult);
        memset(stat, 0, sizeof(Stat));
        GenStat(*stat, result->root);
        return true;
    }
#endif

#if TEST_CONFORMANCE
    virtual bool ParseDouble(const char* input, double* number) const override {
        json::Document root;
        std::string error;
        if (!json::Document::parse(input, root, error) || !root.is_array() ||
            root.array.size() != 1 || !root.array[0].is_number())
            return false;
        *number = root.array[0].num;
        return true;
    }

    virtual bool ParseString(const char* input, std::string& string) const override {
        json::Document root;
        std::string error;
        if (!json::Document::parse(input, root, error) || !root.is_array() ||
            root.array.size() != 1 || !root.array[0].is_string())
            return false;
        string = root.array[0].string;
        return true;
    }
#endif
};

REGISTER_TEST(JsonicTest);

} // namespace
